{-# LANGUAGE OverloadedStrings #-}

-- | Traceable experiment metrics for research posts.
--
-- Posts opt in with an @experiment@ front-matter field.  The value names a
-- directory under @research/@ whose versioned @metrics.json@ is loaded through
-- Hakyll (rather than with a raw filesystem read), so incremental builds track
-- changes to the metrics artifact.  A bracketed Pandoc span such as
-- @[accepted]{.metric}@ is then replaced by that metric's deterministically
-- formatted value.  Missing, malformed, or mismatched data is a hard compiler
-- error.
module Blog.Metrics
  ( MetricsDocument
  , loadPostMetrics
  , metricsCompiler
  , metricFilter
  , parseMetricsDocument
  , resolveMetric
  , resolveMetricInline
  , validateExperiment
  ) where

import Control.Monad (when)
import Data.Aeson
  ( FromJSON (parseJSON)
  , Object
  , Value (..)
  , eitherDecode'
  , withObject
  , (.:)
  )
import qualified Data.Aeson.Types as Aeson
import qualified Data.Aeson.Key as Key
import qualified Data.Aeson.KeyMap as KeyMap
import qualified Data.ByteString.Lazy as BL
import Data.Char (isAsciiLower, isDigit, isHexDigit, isSpace)
import qualified Data.Map.Strict as Map
import Data.Map.Strict (Map)
import Data.Maybe (isJust)
import Data.Scientific
  ( FPFormat (Exponent, Fixed, Generic)
  , Scientific
  , base10Exponent
  , coefficient
  , formatScientific
  )
import Data.Text (Text)
import qualified Data.Text as T
import qualified Data.Text.Encoding as TE
import Data.Time (UTCTime)
import Data.Time.Format (defaultTimeLocale, parseTimeM)
import Hakyll
  ( Compiler
  , Item
  , getMetadata
  , getResourceBody
  , getUnderlying
  , loadBody
  , lookupString
  , fromFilePath
  , itemBody
  )
import Text.Pandoc.Definition (Inline (..))

-- | The complete, validated metrics artifact for one experiment.
data MetricsDocument = MetricsDocument
  { documentSchemaVersion :: Int
  , documentExperiment    :: Text
  , documentProvenance    :: Provenance
  , documentMetrics       :: Map Text Metric
  } deriving (Eq, Show)

data Provenance = Provenance
  { provenanceGeneratedAt :: Text
  , provenanceGenerator   :: FilePath
  , provenanceInputs      :: [ProvenanceInput]
  } deriving (Eq, Show)

data ProvenanceInput = ProvenanceInput
  { provenanceInputPath   :: FilePath
  , provenanceInputSha256 :: Text
  } deriving (Eq, Show)

data Metric = Metric
  { metricType        :: MetricType
  , metricValue       :: MetricValue
  , metricFormat      :: Maybe MetricFormat
  , metricDescription :: Text
  , metricUnit        :: Maybe Text
  } deriving (Eq, Show)

data MetricType = MetricInteger | MetricNumber | MetricBoolean
  deriving (Eq, Show)

data MetricValue
  = IntegerValue Integer
  | NumberValue Scientific
  | BooleanValue Bool
  deriving (Eq, Show)

data MetricFormat
  = FixedFormat Int
  | ScientificFormat Int
  | PercentFormat Int
  | RawFormat
  deriving (Eq, Show)

instance FromJSON MetricsDocument where
  parseJSON = withObject "metrics document" $ \o -> do
    rejectUnknown "metrics document"
      ["schema_version", "experiment", "provenance", "metrics"] o
    MetricsDocument
      <$> o .: "schema_version"
      <*> o .: "experiment"
      <*> o .: "provenance"
      <*> o .: "metrics"

instance FromJSON Provenance where
  parseJSON = withObject "metrics provenance" $ \o -> do
    rejectUnknown "metrics provenance" ["generated_at", "generator", "inputs"] o
    Provenance
      <$> o .: "generated_at"
      <*> o .: "generator"
      <*> o .: "inputs"

instance FromJSON ProvenanceInput where
  parseJSON = withObject "metrics provenance input" $ \o -> do
    rejectUnknown "metrics provenance input" ["path", "sha256"] o
    ProvenanceInput
      <$> o .: "path"
      <*> o .: "sha256"

instance FromJSON Metric where
  parseJSON = withObject "metric" $ \o -> do
    rejectUnknown "metric" ["type", "value", "format", "description", "unit"] o
    typeName <- o .: "type" :: Aeson.Parser Text
    value <- o .: "value"
    format <- parseOptionalField "format" o
    description <- o .: "description"
    unit <- parseOptionalField "unit" o
    (kind, parsedValue) <- parseMetricValue typeName value
    validateFormatForType kind format
    pure $ Metric kind parsedValue format description unit

instance FromJSON MetricFormat where
  parseJSON = withObject "metric format" $ \o -> do
    rejectUnknown "metric format" ["style", "digits"] o
    style <- o .: "style" :: Aeson.Parser Text
    digits <- parseOptionalField "digits" o
    case (style, digits) of
      ("fixed", Just count)      -> boundedDigits FixedFormat count
      ("scientific", Just count) -> boundedDigits ScientificFormat count
      ("percent", Just count)    -> boundedDigits PercentFormat count
      ("raw", Nothing)           -> pure RawFormat
      ("raw", Just _)            -> fail "raw metric format does not accept digits"
      (known, Nothing)
        | known `elem` ["fixed", "scientific", "percent"] ->
            fail $ T.unpack known ++ " metric format requires digits"
      _ -> fail $ "unsupported metric format " ++ T.unpack style

boundedDigits :: (Int -> MetricFormat) -> Int -> Aeson.Parser MetricFormat
boundedDigits constructor count
  | count >= 0 && count <= 12 = pure (constructor count)
  | otherwise = fail "metric format digits must be between 0 and 12"

validateFormatForType :: MetricType -> Maybe MetricFormat -> Aeson.Parser ()
validateFormatForType MetricNumber Nothing =
  fail "number metrics require a format"
validateFormatForType MetricNumber (Just _) = pure ()
validateFormatForType _ Nothing = pure ()
validateFormatForType _ (Just _) =
  fail "only number metrics accept a format"

parseMetricValue :: Text -> Value -> Aeson.Parser (MetricType, MetricValue)
parseMetricValue "integer" (Number n) = do
  integerValue <- parseBoundedInteger n
  pure (MetricInteger, IntegerValue integerValue)
parseMetricValue "number" (Number n) =
  pure (MetricNumber, NumberValue n)
parseMetricValue "boolean" (Bool b) =
  pure (MetricBoolean, BooleanValue b)
parseMetricValue kind _
  | kind `elem` ["integer", "number", "boolean"] =
      fail $ "metric value does not match declared type " ++ T.unpack kind
  | otherwise =
      fail $ "unsupported metric type " ++ T.unpack kind

-- Convert an integral Scientific only after proving that its decimal expansion
-- is small.  This avoids expanding a compact value such as @1e100000000@ into
-- a hundred-million-digit 'Integer' while decoding an untrusted artifact.
parseBoundedInteger :: Scientific -> Aeson.Parser Integer
parseBoundedInteger value
  | rawCoefficient == 0 = pure 0
  | coefficientDigits > 256 = fail "integer metric has an unreasonably large coefficient"
  | scientificExponent >= 0 = do
      let outputLength = signLength + coefficientDigits + toInteger scientificExponent
      when (outputLength > 128) $
        fail "integer metric exceeds 128 formatted characters"
      pure $ rawCoefficient * (10 ^ scientificExponent)
  | decimalPlaces >= coefficientDigits =
      fail "metric type is integer but value is not an integer"
  | otherwise =
      let divisor = 10 ^ decimalPlaces
          (integerValue, remainder) = rawCoefficient `quotRem` divisor
          outputLength = signLength + integerDigits integerValue
      in if remainder /= 0
          then fail "metric type is integer but value is not an integer"
          else if outputLength > 128
            then fail "integer metric exceeds 128 formatted characters"
            else pure integerValue
  where
    rawCoefficient = coefficient value
    scientificExponent = base10Exponent value
    coefficientDigits = integerDigits rawCoefficient
    decimalPlaces = negate (toInteger scientificExponent)
    signLength = if rawCoefficient < 0 then 1 else 0

rejectUnknown
  :: String -> [Text] -> KeyMap.KeyMap Value -> Aeson.Parser ()
rejectUnknown label allowed object =
  case filter (`notElem` allowed) (map Key.toText (KeyMap.keys object)) of
    [] -> pure ()
    unknown -> fail $ label ++ " has unknown field(s): "
      ++ T.unpack (T.intercalate ", " unknown)

parseOptionalField :: FromJSON value => Text -> Object -> Aeson.Parser (Maybe value)
parseOptionalField field object =
  case KeyMap.lookup (Key.fromText field) object of
    Nothing -> pure Nothing
    Just Null -> fail $ T.unpack field ++ " must not be null"
    Just value -> Just <$> parseJSON value

-- | Decode and validate one complete metrics artifact.
parseMetricsDocument :: String -> Either String MetricsDocument
parseMetricsDocument input = do
  document <- eitherDecode' (BL.fromStrict (TE.encodeUtf8 (T.pack input)))
  validateDocument document
  pure document

validateDocument :: MetricsDocument -> Either String ()
validateDocument document = do
  unlessEither (documentSchemaVersion document == 1)
    "schema_version must be 1"
  validateExperiment (documentExperiment document)
  validateProvenance (documentProvenance document)
  unlessEither (not (Map.null (documentMetrics document)))
    "metrics must contain at least one entry"
  mapM_ validateNamedMetric (Map.toList (documentMetrics document))

validateProvenance :: Provenance -> Either String ()
validateProvenance provenance = do
  let generatedAt = provenanceGeneratedAt provenance
      generator = provenanceGenerator provenance
  unlessEither (looksLikeUtcTimestamp generatedAt)
    "provenance.generated_at must be a UTC timestamp such as 2026-07-19T20:00:00Z"
  validateRelativePath "provenance.generator" generator
  unlessEither (not (null (provenanceInputs provenance)))
    "provenance.inputs must contain at least one fingerprinted input"
  mapM_ validateInput (provenanceInputs provenance)

validateInput :: ProvenanceInput -> Either String ()
validateInput input = do
  validateRelativePath "provenance input path" (provenanceInputPath input)
  let digest = provenanceInputSha256 input
  unlessEither (T.length digest == 64 && T.all isHexDigit digest)
    ("invalid SHA-256 for provenance input " ++ provenanceInputPath input)

validateNamedMetric :: (Text, Metric) -> Either String ()
validateNamedMetric (name, metric) = do
  unlessEither (validMetricName name)
    ("invalid metric name " ++ T.unpack name)
  unlessEither (not (T.null (T.strip (metricDescription metric))))
    ("description for metric " ++ T.unpack name ++ " must not be empty")
  case metricUnit metric of
    Nothing -> pure ()
    Just unit -> validateInlineText ("unit for metric " <> name) unit
  validateMetricRenderSize name metric
  unlessEither (T.length (renderMetric metric) <= 128)
    ("formatted value for metric " ++ T.unpack name ++ " exceeds 128 characters")

-- Bound fixed-point expansion before calling 'formatScientific'.  Scientific
-- notation such as @1e100000000@ is compact in JSON but fixed rendering would
-- otherwise attempt to allocate a hundred-million-character string.
validateMetricRenderSize :: Text -> Metric -> Either String ()
validateMetricRenderSize name metric =
  case (metricValue metric, metricFormat metric) of
    (NumberValue value, Just (FixedFormat digits)) ->
      validateFixedSize value digits
    (NumberValue value, Just (PercentFormat digits)) ->
      validateFixedSize (value * 100) digits
    (NumberValue value, _) ->
      validateCoefficientSize value
    _ -> pure ()
  where
    label = "numeric value for metric " ++ T.unpack name
    validateCoefficientSize value =
      unlessEither (integerDigits (coefficient value) <= 256)
        (label ++ " has an unreasonably large coefficient")
    validateFixedSize value digits = do
      validateCoefficientSize value
      unlessEither (estimatedFixedLength value digits <= 256)
        (label ++ " would produce an unreasonably large fixed value")

integerDigits :: Integer -> Integer
integerDigits value = toInteger (length (show (abs value)))

-- Conservative upper bound including sign and a possible rounding carry.
estimatedFixedLength :: Scientific -> Int -> Integer
estimatedFixedLength value digits
  | coefficient value == 0 = signLength + 1 + fractionLength
  | otherwise =
      signLength
        + max 1 (integerDigits (coefficient value) + toInteger (base10Exponent value))
        + fractionLength
        + 1
  where
    signLength = if coefficient value < 0 then 1 else 0
    fractionLength = if digits == 0 then 0 else 1 + toInteger digits

validateInlineText :: Text -> Text -> Either String ()
validateInlineText label value =
  unlessEither
    (not (T.null (T.strip value)) && T.all (not . (`elem` ['\n', '\r', '\t'])) value)
    (T.unpack label ++ " must be non-empty inline text")

-- | Validate the canonical one-directory experiment slug used in front matter.
validateExperiment :: Text -> Either String ()
validateExperiment slug =
  unlessEither (validExperimentSlug slug) $ T.unpack slug
    ++ " is not a valid experiment slug (use lowercase ASCII letters, digits, and single hyphens)"

validExperimentSlug :: Text -> Bool
validExperimentSlug slug =
  case T.uncons slug of
    Nothing -> False
    Just (first, rest) ->
      isAsciiLower first
        && T.all validRest rest
        && T.last slug /= '-'
        && not ("--" `T.isInfixOf` slug)
  where
    validRest c = isAsciiLower c || isDigit c || c == '-'

validMetricName :: Text -> Bool
validMetricName name =
  case T.uncons name of
    Nothing -> False
    Just (first, rest) ->
      isAsciiLower first && T.all validRest rest
  where
    validRest c = isAsciiLower c || isDigit c || c == '_'

looksLikeUtcTimestamp :: Text -> Bool
looksLikeUtcTimestamp value =
  T.length value == 20
    && T.index value 4 == '-'
    && T.index value 7 == '-'
    && T.index value 10 == 'T'
    && T.index value 13 == ':'
    && T.index value 16 == ':'
    && T.last value == 'Z'
    && isJust
      ( parseTimeM True defaultTimeLocale "%Y-%m-%dT%H:%M:%SZ" (T.unpack value)
          :: Maybe UTCTime
      )

validateRelativePath :: String -> FilePath -> Either String ()
validateRelativePath label path =
  unlessEither
    ( not (null path)
      && take 1 path /= "/"
      && '\\' `notElem` path
      && not (".." `elem` splitOnSlash path)
      && not (any isSpace path)
    )
    (label ++ " must be a space-free repository-relative path without '..'")

splitOnSlash :: String -> [String]
splitOnSlash [] = [""]
splitOnSlash value =
  let (part, rest) = break (== '/') value
  in part : case rest of
      []       -> []
      (_ : xs) -> splitOnSlash xs

unlessEither :: Bool -> String -> Either String ()
unlessEither condition message =
  if condition then Right () else Left message

-- | Load the metrics artifact selected by the current post's front matter.
-- Loading it as a Hakyll item records the dependency for incremental builds.
loadPostMetrics :: Compiler (Maybe MetricsDocument)
loadPostMetrics = do
  post <- getUnderlying
  metadata <- getMetadata post
  case lookupString "experiment" metadata of
    Nothing -> pure Nothing
    Just rawSlug -> do
      let slug = T.pack rawSlug
      case validateExperiment slug of
        Left err -> fail $ "[metrics] " ++ err
        Right () -> pure ()
      let metricsPath = "research/" ++ rawSlug ++ "/metrics.json"
      body <- loadBody (fromFilePath metricsPath)
      case parseMetricsDocument body of
        Left err -> fail $ "[metrics] " ++ metricsPath ++ ": " ++ err
        Right document -> do
          when (documentExperiment document /= slug) $
            fail $ "[metrics] " ++ metricsPath ++ ": experiment is "
              ++ T.unpack (documentExperiment document) ++ ", expected " ++ rawSlug
          pure (Just document)

-- | Validate every metrics artifact that Hakyll routes onto the public site.
-- A work-in-progress file should use a different name (for example,
-- @metrics.example.json@) until it satisfies the publication schema.
metricsCompiler :: Compiler (Item String)
metricsCompiler = do
  item <- getResourceBody
  case parseMetricsDocument (itemBody item) of
    Left err -> fail $ "[metrics] " ++ err
    Right _ -> pure item

-- | Look up the deterministically formatted string for one named result.
resolveMetric :: MetricsDocument -> Text -> Either String Text
resolveMetric document name =
  case Map.lookup name (documentMetrics document) of
    Nothing -> Left $ "unknown metric " ++ T.unpack name
      ++ " for experiment " ++ T.unpack (documentExperiment document)
    Just metric -> Right (renderMetric metric)

renderMetric :: Metric -> Text
renderMetric metric =
  case (metricValue metric, metricFormat metric) of
    (IntegerValue value, Nothing) -> T.pack (show value)
    (NumberValue value, Just format) -> renderNumber format value
    (BooleanValue value, Nothing) -> if value then "true" else "false"
    -- Parsing rejects every other combination.
    _ -> "[invalid metric]"

renderNumber :: MetricFormat -> Scientific -> Text
renderNumber (FixedFormat digits) value =
  T.pack (formatScientific Fixed (Just digits) value)
renderNumber (PercentFormat digits) value =
  T.pack (formatScientific Fixed (Just digits) (value * 100)) <> "%"
renderNumber RawFormat value =
  T.pack (formatScientific Generic Nothing value)
renderNumber (ScientificFormat digits) value =
  let rendered = T.pack (formatScientific Exponent (Just digits) value)
      (coefficientText, exponentWithMarker) = T.breakOn "e" rendered
  in if T.null exponentWithMarker
      then rendered
      else coefficientText <> "×10" <> T.map superscript (T.drop 1 exponentWithMarker)

superscript :: Char -> Char
superscript '-' = '⁻'
superscript '+' = '⁺'
superscript '0' = '⁰'
superscript '1' = '¹'
superscript '2' = '²'
superscript '3' = '³'
superscript '4' = '⁴'
superscript '5' = '⁵'
superscript '6' = '⁶'
superscript '7' = '⁷'
superscript '8' = '⁸'
superscript '9' = '⁹'
superscript other = other

-- | Resolve a Pandoc metric span, leaving every other inline untouched.
resolveMetricInline :: Maybe MetricsDocument -> Inline -> Either String Inline
resolveMetricInline metrics (Span attributes@(_, classes, _) contents)
  | "metric" `elem` classes = do
      unlessEither (attributes == ("", ["metric"], []))
        "metric references must not have an id, extra classes, or attributes"
      name <- case contents of
        [Str value] | validMetricName value -> Right value
        _ -> Left "metric references must use [metric-name]{.metric} with a valid metric name"
      document <- case metrics of
        Nothing -> Left $ "metric reference " ++ T.unpack name
          ++ " requires an experiment field in the post front matter"
        Just value -> Right value
      display <- resolveMetric document name
      Right $ Span
        ("", ["metric-value"], [("data-metric", name)])
        [Str display]
resolveMetricInline _ inline = Right inline

-- | Compiler wrapper that turns traceability failures into hard build errors.
metricFilter :: Maybe MetricsDocument -> Inline -> Compiler Inline
metricFilter metrics inline =
  case resolveMetricInline metrics inline of
    Left err -> fail $ "[metrics] " ++ err
    Right resolved -> pure resolved

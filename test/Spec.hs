-- | Minimal test-suite for the pure helpers in the @blog@ library.
-- Depends only on the library and its own deps (pandoc-types, text) so it
-- adds no extra snapshot packages and runs fast in CI.
module Main (main) where

import Blog.Compilers (wrapTables)
import Blog.Metrics
  ( MetricsDocument
  , parseMetricsDocument
  , resolveMetric
  , resolveMetricInline
  , validateExperiment
  )
import Blog.TikZ (inlineSvg, namespaceIds)
import Control.Monad (forM_, unless)
import qualified Data.Text as T
import System.Exit (exitFailure)
import Text.Pandoc.Definition
  ( Block (..), Caption (..), Inline (..), TableFoot (..), TableHead (..), nullAttr )

validMetricsJson :: String
validMetricsJson = unlines
  [ "{"
  , "  \"schema_version\": 1,"
  , "  \"experiment\": \"example-experiment\","
  , "  \"provenance\": {"
  , "    \"generated_at\": \"2026-07-19T20:00:00Z\","
  , "    \"generator\": \"research/example-experiment/generate-metrics.mjs\","
  , "    \"inputs\": [{"
  , "      \"path\": \"research/example-experiment/results.json\","
  , "      \"sha256\": \"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\""
  , "    }]"
  , "  },"
  , "  \"metrics\": {"
  , "    \"fixed_value\": {"
  , "      \"type\": \"number\", \"value\": 1.0822109633152537,"
  , "      \"format\": {\"style\": \"fixed\", \"digits\": 4},"
  , "      \"description\": \"A fixed result\""
  , "    },"
  , "    \"scientific_value\": {"
  , "      \"type\": \"number\", \"value\": 0.000035003436828022786,"
  , "      \"format\": {\"style\": \"scientific\", \"digits\": 1},"
  , "      \"description\": \"A scientific result\""
  , "    },"
  , "    \"percent_value\": {"
  , "      \"type\": \"number\", \"value\": 0.954,"
  , "      \"format\": {\"style\": \"percent\", \"digits\": 1},"
  , "      \"description\": \"A percentage\""
  , "    },"
  , "    \"accepted\": {"
  , "      \"type\": \"integer\", \"value\": 35,"
  , "      \"description\": \"Accepted calls\""
  , "    },"
  , "    \"expanded\": {"
  , "      \"type\": \"boolean\", \"value\": false,"
  , "      \"description\": \"Expansion gate\""
  , "    }"
  , "  }"
  , "}"
  ]

invalidSchemaJson :: String
invalidSchemaJson = unlines
  [ "{"
  , "  \"schema_version\": 2,"
  , "  \"experiment\": \"example-experiment\","
  , "  \"provenance\": {"
  , "    \"generated_at\": \"2026-07-19T20:00:00Z\","
  , "    \"generator\": \"generate.mjs\","
  , "    \"inputs\": [{\"path\": \"input.json\", \"sha256\": \"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\"}]"
  , "  },"
  , "  \"metrics\": {\"value\": {\"type\": \"integer\", \"value\": 1, \"description\": \"test\"}}"
  , "}"
  ]

invalidDisplayJson :: String
invalidDisplayJson = unlines
  [ "{"
  , "  \"schema_version\": 1,"
  , "  \"experiment\": \"example-experiment\","
  , "  \"provenance\": {"
  , "    \"generated_at\": \"2026-07-19T20:00:00Z\","
  , "    \"generator\": \"generate.mjs\","
  , "    \"inputs\": [{\"path\": \"input.json\", \"sha256\": \"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\"}]"
  , "  },"
  , "  \"metrics\": {\"value\": {"
  , "    \"type\": \"number\", \"value\": 0.89, \"display\": \"9.99\","
  , "    \"format\": {\"style\": \"fixed\", \"digits\": 2}, \"description\": \"test\""
  , "  }}"
  , "}"
  ]

withMetrics :: (MetricsDocument -> Bool) -> Bool
withMetrics check = either (const False) check (parseMetricsDocument validMetricsJson)

rejects :: String -> Bool
rejects = either (const True) (const False) . parseMetricsDocument

replaceText :: String -> String -> String -> String
replaceText old new =
  T.unpack . T.replace (T.pack old) (T.pack new) . T.pack

-- | A minimal, content-free table for exercising 'wrapTables'.
emptyTable :: Block
emptyTable =
  Table nullAttr (Caption Nothing []) []
        (TableHead nullAttr []) [] (TableFoot nullAttr [])

-- | (name, condition) — each must hold.
checks :: [(String, Bool)]
checks =
  [ ( "inlineSvg strips the XML prolog"
    , inlineSvg "<?xml version=\"1.0\"?>\n<svg>x</svg>" == "<svg>x</svg>"
    )
  , ( "inlineSvg leaves prolog-free markup unchanged"
    , inlineSvg "<svg>y</svg>" == "<svg>y</svg>"
    )
  , ( "inlineSvg passes through input with no <svg> tag"
    , inlineSvg "not an svg" == "not an svg"
    )
  , ( "namespaceIds prefixes a glyph id and its reference identically"
    , namespaceIds (T.pack "n7") (T.pack "<path id='g3-1'/><use xlink:href='#g3-1'/>")
        == T.pack "<path id='n7g3-1'/><use xlink:href='#n7g3-1'/>"
    )
  , ( "namespaceIds prefixes clip-path id and its url() reference"
    , namespaceIds (T.pack "n7") (T.pack "<clipPath id=\"c1\"><g clip-path=\"url(#c1)\">")
        == T.pack "<clipPath id=\"n7c1\"><g clip-path=\"url(#n7c1)\">"
    )
  , ( "wrapTables wraps a table in div.table-scroll"
    , wrapTables emptyTable == Div ("", ["table-scroll"], []) [emptyTable]
    )
  , ( "wrapTables leaves non-table blocks unchanged"
    , wrapTables (Para []) == Para []
    )
  , ( "metrics schema parses a valid typed artifact"
    , withMetrics (const True)
    )
  , ( "metrics schema rejects unsupported versions"
    , rejects invalidSchemaJson
    )
  , ( "metrics schema rejects free-form display text"
    , rejects invalidDisplayJson
    )
  , ( "metrics parser preserves UTF-8 metadata"
    , either (const False) (const True) . parseMetricsDocument $
        replaceText "A fixed result" "A μ result" validMetricsJson
    )
  , ( "metrics schema rejects impossible UTC timestamps"
    , rejects $ replaceText
        "2026-07-19T20:00:00Z" "2026-13-40T25:61:61Z" validMetricsJson
    )
  , ( "metrics schema rejects malformed provenance hashes"
    , rejects $ replaceText
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        validMetricsJson
    )
  , ( "metrics schema rejects provenance path traversal"
    , rejects $ replaceText
        "research/example-experiment/results.json"
        "../private/results.json"
        validMetricsJson
    )
  , ( "metrics schema rejects fractional integer values"
    , rejects $ replaceText
        "\"type\": \"integer\", \"value\": 35"
        "\"type\": \"integer\", \"value\": 35.5"
        validMetricsJson
    )
  , ( "metrics schema bounds compact integer exponents before expansion"
    , rejects $ replaceText
        "\"type\": \"integer\", \"value\": 35"
        "\"type\": \"integer\", \"value\": 1e100000000"
        validMetricsJson
    )
  , ( "metrics schema rejects null optional fields"
    , rejects $ replaceText
        "\"description\": \"Accepted calls\""
        "\"description\": \"Accepted calls\", \"unit\": null"
        validMetricsJson
    )
  , ( "metrics schema rejects unknown fields"
    , rejects $ replaceText
        "\"description\": \"Accepted calls\""
        "\"description\": \"Accepted calls\", \"typo\": 1"
        validMetricsJson
    )
  , ( "metrics schema rejects a value that disagrees with its type"
    , rejects $ replaceText
        "\"type\": \"boolean\", \"value\": false"
        "\"type\": \"boolean\", \"value\": \"false\""
        validMetricsJson
    )
  , ( "metrics schema rejects numeric formatting on an integer"
    , rejects $ replaceText
        "\"type\": \"integer\", \"value\": 35,"
        "\"type\": \"integer\", \"value\": 35, \"format\": {\"style\": \"fixed\", \"digits\": 0},"
        validMetricsJson
    )
  , ( "metrics schema bounds display precision"
    , rejects $ replaceText
        "\"style\": \"fixed\", \"digits\": 4"
        "\"style\": \"fixed\", \"digits\": 13"
        validMetricsJson
    )
  , ( "metrics schema bounds formatted output length"
    , rejects $ replaceText
        "\"type\": \"number\", \"value\": 1.0822109633152537"
        "\"type\": \"number\", \"value\": 1e100000000"
        validMetricsJson
    )
  , ( "experiment slugs reject path traversal"
    , either (const True) (const False) (validateExperiment "../secret")
    )
  , ( "fixed metric formatting is derived from the numeric value"
    , withMetrics $ \metrics -> resolveMetric metrics "fixed_value" == Right "1.0822"
    )
  , ( "scientific metric formatting uses a deterministic Unicode exponent"
    , withMetrics $ \metrics -> resolveMetric metrics "scientific_value" == Right "3.5×10⁻⁵"
    )
  , ( "percentage formatting is derived from the numeric ratio"
    , withMetrics $ \metrics -> resolveMetric metrics "percent_value" == Right "95.4%"
    )
  , ( "integer and boolean metrics render without a free-form display"
    , withMetrics $ \metrics ->
        resolveMetric metrics "accepted" == Right "35"
          && resolveMetric metrics "expanded" == Right "false"
    )
  , ( "metric spans become traceable metric-value spans"
    , withMetrics $ \metrics ->
        resolveMetricInline
          (Just metrics)
          (Span ("", ["metric"], []) [Str "accepted"])
        == Right
          (Span ("", ["metric-value"], [("data-metric", "accepted")]) [Str "35"])
    )
  , ( "a metric span without experiment metadata fails"
    , either (const True) (const False) $
        resolveMetricInline Nothing (Span ("", ["metric"], []) [Str "accepted"])
    )
  , ( "metric spans reject extra attributes"
    , withMetrics $ \metrics ->
        either (const True) (const False) $
          resolveMetricInline
            (Just metrics)
            (Span ("", ["metric", "extra"], []) [Str "accepted"])
    )
  , ( "metric spans reject anything except one metric-name token"
    , withMetrics $ \metrics ->
        either (const True) (const False) $
          resolveMetricInline
            (Just metrics)
            (Span ("", ["metric"], []) [Str "accepted", Space, Str "calls"])
    )
  , ( "an unknown metric name fails"
    , withMetrics $ \metrics ->
        either (const True) (const False) (resolveMetric metrics "missing")
    )
  , ( "ordinary inline code is untouched"
    , resolveMetricInline Nothing (Code nullAttr "[accepted]{.metric}")
        == Right (Code nullAttr "[accepted]{.metric}")
    )
  ]

main :: IO ()
main = do
  let failures = [name | (name, ok) <- checks, not ok]
  forM_ checks $ \(name, ok) ->
    putStrLn $ (if ok then "ok   - " else "FAIL - ") ++ name
  unless (null failures) exitFailure

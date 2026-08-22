-- | Shared template contexts.
module Blog.Context
  ( postCtx
  , baseCtx
  , hasFigure
  , figureImageSrc
  , figureImageAlt
  , OgImageInputs (..)
  , resolveOgImage
  ) where

import Control.Applicative ((<|>))
import Data.Char (toLower)
import Data.List (isInfixOf, isPrefixOf, isSuffixOf)
import Data.Maybe (fromMaybe)
import Hakyll
import System.Directory (doesFileExist)

import Blog.Metrics (loadPostMetricsFor)

-- | Canonical origin for absolute URLs (og:url, og:image). Card scrapers do not
-- resolve relative URLs, so social meta must be absolutized against this.
siteHost :: String
siteHost = "https://pvjohnston.com"

-- | Fallback description used for social meta on pages without their own.
siteDescription :: String
siteDescription =
  "Peter V. Johnston is an analytical problem solver, AI-assisted tool builder, and Ph.D. chemist who makes complicated domains legible."

-- | Fallback description of the branded social image used when a page does not
-- have a note-specific card.
siteImageAlt :: String
siteImageAlt =
  "Peter V. Johnston — analytical problem solver, AI-assisted tool builder, and Ph.D. chemist"

-- | Site-relative path of the generic branded card. Non-note pages keep this.
genericOgImagePath :: String
genericOgImagePath = "/images/og-image.png"

-- | Fields every page that renders @templates/default.html@ needs: the social
-- @ogimage@ (absolute, per-post overridable), its @ogimagealt@ text, and the
-- site-description fallback, over the Hakyll defaults. Used directly for
-- static pages / index / archive, and folded into 'postCtx'.
baseCtx :: Context String
baseCtx =
  ogImageField <>
  ogImageAltField <>
  constField "siteHost" siteHost <>
  constField "sitedesc" siteDescription <>
  defaultContext

-- | Inputs 'resolveOgImage' needs. The generated-card path is @Just@ only when
-- that file exists on disk; the field compiler performs that check.
data OgImageInputs = OgImageInputs
  { ogiExplicit     :: Maybe String
  , ogiFigure       :: Maybe String
  , ogiTitle        :: Maybe String
  , ogiGeneratedRel :: Maybe String
  }

-- | Pick a share image and its alt text.
--
-- Order: explicit @og-image@ front matter, then a generated
-- @images\/\<slug\>-og.png@ card, then the @figure@ metadata @src@, then the
-- generic branded card. Alt text prefers the figure's @alt@, then the note
-- title, then the branded-card description.
resolveOgImage :: OgImageInputs -> (String, String)
resolveOgImage (OgImageInputs explicit figure title generated) =
  case explicit of
    Just u -> (absolutize u, noteAlt)
    Nothing ->
      case generated of
        Just p -> (absolutize p, noteAlt)
        Nothing ->
          case figure >>= figureImageSrc of
            Just src -> (absolutize src, fromMaybe siteImageAlt (figure >>= figureImageAlt))
            Nothing  -> (absolutize genericOgImagePath, siteImageAlt)
  where
    noteAlt = fromMaybe siteImageAlt ((figure >>= figureImageAlt) <|> title)

-- | Absolute URL of a page's share image. Notes resolve per 'resolveOgImage';
-- home, about, and other non-note pages keep the generic branded card.
ogImageField :: Context a
ogImageField = field "ogimage" $ \item -> fst <$> ogImageFromItem item

-- | Alt text for a page's share image. See 'resolveOgImage'.
ogImageAltField :: Context a
ogImageAltField = field "ogimagealt" $ \item -> snd <$> ogImageFromItem item

ogImageFromItem :: Item a -> Compiler (String, String)
ogImageFromItem item = do
  let ident = itemIdentifier item
  explicit <- getMetadataField ident "og-image"
  figure   <- getMetadataField ident "figure"
  title    <- getMetadataField ident "title"
  generated <- case generatedOgRelPath ident of
    Nothing -> pure Nothing
    Just p  -> do
      exists <- unsafeCompiler (doesFileExist p)
      pure (if exists then Just ("/" ++ p) else Nothing)
  pure $ resolveOgImage (OgImageInputs explicit figure title generated)

-- | Conventional generated card for a post identifier: @images\/\<slug\>-og.png@.
-- 'Nothing' on non-post pages so they never claim a per-note card.
generatedOgRelPath :: Identifier -> Maybe FilePath
generatedOgRelPath ident
  | "posts/" `isPrefixOf` path = Just ("images/" ++ stripPostExt (drop 6 path) ++ "-og.png")
  | otherwise                  = Nothing
  where
    path = toFilePath ident
    stripPostExt name
      | ".markdown" `isSuffixOf` name = take (length name - 9) name
      | ".md"       `isSuffixOf` name = take (length name - 3) name
      | otherwise                     = name

-- | Turn a site-relative path or absolute URL into the host-qualified form
-- card scrapers require.
absolutize :: String -> String
absolutize u
  | "http://"  `isPrefixOf` u = u
  | "https://" `isPrefixOf` u = u
  | "/"        `isPrefixOf` u = siteHost ++ u
  | otherwise                 = siteHost ++ "/" ++ u

-- | Extract the conventional @src="…"@ (or single-quoted equivalent) from
-- the image HTML stored in @figure@ metadata.
figureImageSrc :: String -> Maybe String
figureImageSrc html = quotedAttr "src" html

-- | Extract the conventional @alt="…"@ (or single-quoted equivalent) from
-- the image HTML stored in @figure@ metadata.
figureImageAlt :: String -> Maybe String
figureImageAlt html = case quotedAttr "alt" html of
  Just alt | '"' `elem` alt -> Just (escapeDoubleQuotes alt)
  other                     -> other
  where
    -- The destination meta tag is double-quoted. A raw double quote is
    -- impossible in the conventional double-quoted source form, but must be
    -- encoded when the source figure uses single quotes.
    escapeDoubleQuotes = concatMap $ \c ->
      if c == '"' then "&quot;" else [c]

-- | Read an HTML attribute value from @name="…"@ or @name='…'@.
quotedAttr :: String -> String -> Maybe String
quotedAttr name html = extract (" " ++ name ++ "=\"") '"' html
                   <|> extract (" " ++ name ++ "='") '\'' html
  where
    extract marker closing input = do
      (_, atMarker) <- breakOnSub marker input
      let value = drop (length marker) atMarker
          (attr, rest) = break (== closing) value
      if null attr || null rest then Nothing else Just attr

-- | The post's declared form (@post-type@: @research@ / @understanding@),
-- exposed as @postType@ so templates can render the note badge. Withheld when
-- the field is absent, so @$if(postType)$@ is false on posts that predate it.
postTypeField :: Context String
postTypeField = field "postType" $ \item -> do
  mpt <- getMetadataField (itemIdentifier item) "post-type"
  case mpt of
    Just pt -> pure pt
    Nothing -> noResult "no post-type"

-- | Derived traceability mark, emitted (as @"1"@) when the post's @experiment@
-- binding names a metrics artifact that loads and validates. This is the same
-- load the post compiler performs unconditionally, so the badge cannot claim
-- traceability the build did not verify — an invalid artifact fails the build
-- outright (see 'Blog.Metrics').
traceableField :: Context String
traceableField = field "traceable" $ \item -> do
  mdoc <- loadPostMetricsFor (itemIdentifier item)
  case mdoc of
    Just _  -> pure "1"
    Nothing -> noResult "no experiment binding"

-- | Context for posts: a human-readable @date@ field, the derived @topic@ /
-- @topicSlug@ used by the home-page filter pills, the @postType@ note badge,
-- the derived @traceable@ mark, the @article@ og:type marker, plus 'baseCtx'.
--
-- @topic@ is a coarse subject bucket derived from a post's FIRST tag so the
-- Latest filter has a small, stable set of pills instead of one pill per raw
-- tag. The mapping is a plain function (see 'topicBucket') — adjust the keyword
-- table there to re-bucket posts; nothing per-post needs editing.
postCtx :: Context String
postCtx =
  dateField "date" "%B %e, %Y" <>
  topicField "topic"     fst <>
  topicField "topicSlug" snd <>
  postTypeField <>
  traceableField <>
  tagsHtmlField "tagChips" (\t -> "<span class=\"tag-chip\">" ++ t ++ "</span>") <>
  tagsHtmlField "hashTags" (\t -> "<span class=\"row-tag\">#" ++ t ++ "</span>") <>
  figureSlidesCtx <>
  hasFigureField <>
  constField "ogtype" "article" <>
  baseCtx

-- | @$if(hasFigure)$@ marker: emitted (as "1") when a post has a figure the
-- featured panel can show — an explicit @figure@ metadata image or a TikZ
-- figure in its compiled body. The featured reel uses it to mark eligible
-- "Latest" rows; withheld (so @$if$@ is false) otherwise.
hasFigureField :: Context String
hasFigureField = field "hasFigure" $ \item -> do
  yes <- hasFigure item
  if yes then pure "1" else noResult "post has no figure"

-- | Whether a post has a featured-showable figure: explicit @figure@ metadata,
-- or a @<div class="tikz-figure">@ in its compiled @content@ snapshot.
hasFigure :: Item a -> Compiler Bool
hasFigure item = do
  mfig <- getMetadataField (itemIdentifier item) "figure"
  case mfig of
    Just _  -> pure True
    Nothing -> do
      body <- loadSnapshotBody (itemIdentifier item) "content"
      pure ("tikz-figure" `isInfixOf` (body :: String))

-- | The featured panel's figure cycler: the post's REAL figures, extracted
-- from the compiled body snapshot — every @.tikz-figure@ block plus the
-- @<p><em>Figure N.</em> …@ caption that immediately follows it, wrapped as
-- @.fig-slide@s (first one active; js\/figure-cycler.js drives the rest).
-- Both fields are withheld when a post has no figures, so templates can guard
-- with @$if(figSlides)$@; the explicit @figure@ metadata override still wins
-- in the template for posts whose figures aren't TikZ.
figureSlidesCtx :: Context String
figureSlidesCtx = field "figSlides" render <> field "figCount" count
  where
    figuresOf item =
      extractFigures <$> loadSnapshotBody (itemIdentifier item) "content"
    render item = do
      figs <- figuresOf item
      case figs of
        [] -> noResult "post has no extractable figures"
        _  -> pure (concat (zipWith slide [1 :: Int ..] figs))
    count item = do
      figs <- figuresOf item
      if null figs then noResult "post has no extractable figures"
                   else pure (show (length figs))
    slide i (fig, mcap) =
      "<div class=\"fig-slide" ++ (if i == 1 then " is-active" else "") ++ "\">"
        ++ fig
        ++ maybe "" (\c -> "<div class=\"fig-slide-caption\">" ++ c ++ "</div>") mcap
        ++ "</div>"

-- | Scan compiled post HTML for @<div class="tikz-figure">…</div>@ blocks and
-- pair each with the caption paragraph that immediately follows, when that
-- paragraph is a @<p><em>Figure …@ marker. Plain substring scanning — the
-- tikz div wraps a single inline SVG, which cannot contain a nested @</div>@.
extractFigures :: String -> [(String, Maybe String)]
extractFigures = go
  where
    open, divClose, pOpen, pClose, capMark :: String
    open     = "<div class=\"tikz-figure\">"
    divClose = "</div>"
    pOpen    = "<p>"
    pClose   = "</p>"
    capMark  = "<p><em>Figure"
    go s = case breakOnSub open s of
      Nothing -> []
      Just (_, atOpen) ->
        let afterOpen = drop (length open) atOpen
        in case breakOnSub divClose afterOpen of
             Nothing -> []
             Just (inner, atClose) ->
               let rest = drop (length divClose) atClose
                   (mcap, rest') = captionAfter rest
               in (open ++ inner ++ divClose, mcap) : go rest'
    captionAfter s =
      let s' = dropWhile (`elem` (" \t\r\n" :: String)) s
      in if capMark `isPrefixOf` s'
           then case breakOnSub pClose s' of
                  Just (capWithP, atClose) ->
                    (Just (drop (length pOpen) capWithP), drop (length pClose) atClose)
                  Nothing -> (Nothing, s)
           else (Nothing, s)

-- | @breakOnSub pat s@: @Just (before, rest)@ where @rest@ starts at the first
-- occurrence of @pat@; @Nothing@ when @pat@ does not occur.
breakOnSub :: String -> String -> Maybe (String, String)
breakOnSub pat s0 = go 0 s0
  where
    go i s
      | pat `isPrefixOf` s = Just (take i s0, s)
      | null s             = Nothing
      | otherwise          = go (i + 1) (drop 1 s)

-- | Render each of a post's comma-separated tags to an HTML fragment and
-- concatenate. Empty (field withheld) when a post has no @tags@, so callers can
-- guard with @$if(tagChips)$@. Field output is inserted unescaped by Hakyll —
-- tags are author-controlled plain words, so no escaping is applied.
tagsHtmlField :: String -> (String -> String) -> Context a
tagsHtmlField key render = field key $ \item -> do
  mtags <- getMetadataField (itemIdentifier item) "tags"
  case splitTags mtags of
    []   -> noResult "no tags"
    tags -> pure (concatMap render tags)

-- | Split a raw @tags@ string on commas, trimming whitespace and dropping
-- blanks.
splitTags :: Maybe String -> [String]
splitTags Nothing   = []
splitTags (Just cs) = filter (not . null) (map trim (splitOn ',' cs))
  where
    splitOn c s = case break (== c) s of
      (a, [])     -> [a]
      (a, _ : bs) -> a : splitOn c bs

-- | A field that reads the post's first tag and projects the mapped
-- (label, slug) pair through the given selector.
topicField :: String -> ((String, String) -> String) -> Context a
topicField key sel = field key $ \item -> do
  mtags <- getMetadataField (itemIdentifier item) "tags"
  pure (sel (topicBucket (firstTag mtags)))

-- | The first comma-separated tag, trimmed and lower-cased. Empty when a post
-- has no @tags@ (those fall through to the "Engineering" bucket).
firstTag :: Maybe String -> String
firstTag = maybe "" (trim . map toLower . takeWhile (/= ','))

-- | Map a first tag to a (display label, url slug) subject bucket. Keyword
-- table is scanned in order; first substring hit wins; default is Engineering.
topicBucket :: String -> (String, String)
topicBucket t = go table
  where
    go [] = ("Engineering", "engineering")
    go ((kw, bucket) : rest)
      | kw `isInfixOf` t = bucket
      | otherwise        = go rest
    table =
      [ ("chemis",            ("Chemistry",   "chemistry"))
      , ("spectro",           ("Chemistry",   "chemistry"))
      , ("pigment",           ("Chemistry",   "chemistry"))
      , ("water",             ("Chemistry",   "chemistry"))
      , ("optic",             ("Physics",     "physics"))
      , ("quantum mechanics", ("Physics",     "physics"))
      , ("physics",           ("Physics",     "physics"))
      , ("science",           ("Physics",     "physics"))
      , ("math",              ("Mathematics", "mathematics"))
      , ("art",               ("Art",         "art"))
      ]

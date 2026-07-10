-- | Shared template contexts.
module Blog.Context
  ( postCtx
  , baseCtx
  , hasFigure
  ) where

import Data.Char (toLower)
import Data.List (isInfixOf, isPrefixOf)
import Hakyll

-- | Canonical origin for absolute URLs (og:url, og:image). Card scrapers do not
-- resolve relative URLs, so social meta must be absolutized against this.
siteHost :: String
siteHost = "https://pvjohnston.com"

-- | Fallback description used for social meta on pages without their own.
siteDescription :: String
siteDescription =
  "Peter Johnston builds useful systems and writes about chemistry, art, software, and the work of making complicated domains legible."

-- | Fields every page that renders @templates/default.html@ needs: the social
-- @ogimage@ (absolute, per-post overridable) and the site-description fallback,
-- over the Hakyll defaults. Used directly for static pages / index / archive,
-- and folded into 'postCtx'.
baseCtx :: Context String
baseCtx =
  ogImageField <>
  constField "siteHost" siteHost <>
  constField "sitedesc" siteDescription <>
  defaultContext

-- | Absolute URL of a page's share image. Uses the post's optional @og-image@
-- metadata (absolute URL or site-relative path, absolutized) and otherwise the
-- one static branded card at @\/images\/og-image.png@.
ogImageField :: Context a
ogImageField = field "ogimage" $ \item -> do
  mo <- getMetadataField (itemIdentifier item) "og-image"
  pure $ case mo of
    Just u  -> absolutize u
    Nothing -> siteHost ++ "/images/og-image.png"
  where
    absolutize u
      | "http://"  `isPrefixOf` u = u
      | "https://" `isPrefixOf` u = u
      | "/"        `isPrefixOf` u = siteHost ++ u
      | otherwise                 = siteHost ++ "/" ++ u

-- | Context for posts: a human-readable @date@ field, the derived @topic@ /
-- @topicSlug@ used by the home-page filter pills, the @article@ og:type marker,
-- plus 'baseCtx'.
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
  tagsHtmlField "tagChips" (\t -> "<span class=\"tag-chip\">" ++ t ++ "</span>") <>
  tagsHtmlField "hashTags" (\t -> "<span class=\"row-tag\">#" ++ t ++ "</span>") <>
  figureSlidesCtx <>
  hasFigureField <>
  constField "ogtype" "article" <>
  baseCtx

-- | @$if(hasFigure)$@ marker: emitted (as "1") when a post has a figure the
-- featured panel can show — an explicit @figure@ metadata image or a TikZ
-- figure in its compiled body. The random-featured picker uses it to mark
-- eligible "Latest" rows; withheld (so @$if$@ is false) otherwise.
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

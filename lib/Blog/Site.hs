{-# LANGUAGE OverloadedStrings #-}

-- | The Hakyll rule set for the site, assembled from the library's compilers,
-- contexts, and feed configuration.
module Blog.Site
  ( siteRules
  ) where

import Control.Monad     (filterM, forM, forM_)
import Data.Char         (isAsciiLower, isDigit, isSpace, toLower)
import Data.List         (dropWhileEnd, groupBy, intercalate, isPrefixOf, isSuffixOf, nub, sort, sortBy)
import Data.Ord          (Down (..))
import Data.Time         (defaultTimeLocale, formatTime)
import System.Directory  (doesDirectoryExist, doesFileExist, listDirectory)
import Hakyll

import Blog.Compilers (bibtexMathCompiler)
import Blog.Context   (baseCtx, postCtx, hasFigure)
import Blog.Feed      (feedConfiguration, feedCtx)
import Blog.Metrics   (metricsCompiler)

-- | Bibliography inputs for the post compiler.
cslFile, bibFile :: String
cslFile = "bib/style.csl"
bibFile = "bib/bibliography.bib"

-- | The static content pages (everything routed except posts and listings).
staticPages :: [Identifier]
staticPages = ["about.markdown", "resume.markdown", "contact.markdown", "colophon.markdown"]

-- | The writing index and its backwards-compatible archive alias.
writingPages :: [Identifier]
writingPages = ["writing.html", "archive.html"]

-- | True when the frontmatter sets @draft: true@.
isDraft :: Metadata -> Bool
isDraft md = lookupString "draft" md == Just "true"

-- | Paths an experiment manifest may list that another rule already routes.
-- Routing them twice would give one identifier two compilers.
routedElsewhere :: FilePath -> Bool
routedElsewhere path =
       path == "LICENSE"
    || path == "research/metrics.schema.json"
    || "downloads/" `isPrefixOf` path
    || ("research/" `isPrefixOf` path && "/metrics.json" `isSuffixOf` path)

-- | Entries of a @PUBLIC_FILES.txt@: one repository-relative path per line,
-- ignoring @#@ comments and blank lines.
readManifest :: FilePath -> IO [FilePath]
readManifest manifest = do
    contents <- readFile manifest
    pure [ trimmed
         | line <- lines contents
         , let trimmed = dropWhile isSpace (dropWhileEnd isSpace line)
         , not (null trimmed)
         , not ("#" `isPrefixOf` trimmed)
         ]

-- | Every reader-facing experiment file, collected from the @PUBLIC_FILES.txt@
-- manifests under @research/@.  The manifests themselves are published too, so
-- a reader can check what the bundle claims to contain against what it serves.
-- Paths that do not exist are dropped rather than failing the build;
-- @scripts/verify-site.mjs@ reports a manifest entry that never reached
-- @_site@, which catches both a typo and a deleted file.
publicExperimentFiles :: IO [Identifier]
publicExperimentFiles = do
    hasResearch <- doesDirectoryExist "research"
    if not hasResearch then pure [] else do
        entries <- listDirectory "research"
        let candidates = [ "research/" ++ e ++ "/PUBLIC_FILES.txt" | e <- sort entries ]
        manifests <- filterM doesFileExist candidates
        listed <- concat <$> mapM readManifest manifests
        present <- filterM doesFileExist
            (filter (not . routedElsewhere) (nub (sort (manifests ++ listed))))
        pure (map fromFilePath present)

-- | URL-safe form of a tag: lowercased, with every run of non-alphanumeric
-- characters collapsed to a single hyphen. Tag pages route to
-- @tags/<slug>.html@.
slugify :: String -> String
slugify = intercalate "-" . words . map normalize . map toLower
  where normalize c = if isAsciiLower c || isDigit c then c else ' '

-- | Group date-ordered posts by publication year, preserving their order. The
-- year comes from the same date extraction 'dateField' uses, so a post can
-- never land in a year bucket its rendered date disagrees with.
yearGroups :: [Item a] -> Compiler [(String, [Item a])]
yearGroups posts = do
  keyed <- forM posts $ \p -> do
    utc <- getItemUTC defaultTimeLocale (itemIdentifier p)
    pure (formatTime defaultTimeLocale "%Y" utc, p)
  pure [ (y, map snd grp)
       | grp@((y, _) : _) <- groupBy (\a b -> fst a == fst b) keyed ]

-- | Tags used by at least two posts. Singleton tags get no page and no cloud
-- chip: a grouping of one is the post itself, not wayfinding (and singletons
-- are two-thirds of all tags — including them turns the cloud into noise).
publishedTags :: Tags -> [(String, [Identifier])]
publishedTags = filter ((>= 2) . length . snd) . tagsMap

-- | The archive's frequency-ordered tag cloud: chips linking to the tag
-- pages, most-used first (ties alphabetical). Tags are author-controlled
-- plain words, so no escaping is applied (same convention as the post
-- context's tag fields).
tagCloudHtml :: Tags -> String
tagCloudHtml = concatMap chip . sortBy cloudOrder . publishedTags
  where
    chip (tag, ids) =
      "<a class=\"cloud-tag\" href=\"/tags/" ++ slugify tag ++ ".html\">" ++ tag
        ++ " <span class=\"cloud-count\">" ++ show (length ids) ++ "</span></a>"
    cloudOrder (a, xs) (b, ys) =
      compare (Down (length xs)) (Down (length ys)) <> compare a b

-- | The site rules. When the flag is 'True' (@PREVIEW_DRAFTS@ is set, see
-- @app/site.hs@) draft posts are built and listed like any other post so they
-- can be previewed locally; otherwise they are skipped entirely — no page is
-- generated, and they appear in no listing, feed, or sitemap.
siteRules :: Bool -> Rules ()
siteRules previewDrafts = do
    -- Citations
    match (fromGlob cslFile) $ compile cslCompiler
    match (fromGlob bibFile) $ compile biblioCompiler

    match "images/*" $ do
        route   idRoute
        compile copyFileCompiler

    match "js/*" $ do
        route   idRoute
        compile copyFileCompiler

    match "fonts/*" $ do
        route   idRoute
        compile copyFileCompiler

    match "downloads/*" $ do
        route   idRoute
        compile copyFileCompiler

    -- Versioned, generated result artifacts are both compiler inputs and
    -- reader-facing provenance.  Keeping them as Hakyll resources makes a
    -- metrics change invalidate every post that loads it during watch/build.
    match "research/*/metrics.json" $ do
        route   idRoute
        compile metricsCompiler

    match "research/metrics.schema.json" $ do
        route   idRoute
        compile copyFileCompiler

    match "LICENSE" $ do
        route   idRoute
        compile copyFileCompiler

    -- Explicitly reviewed reader-facing files for traceable experiments, read
    -- from each experiment's own PUBLIC_FILES.txt at build time.  Hand-copying
    -- the allowlist into this table is what let three of five bundles 404: the
    -- manifest advertised files the build never routed.  Deriving the table
    -- from the manifest makes that drift impossible.  LICENSE, metrics.json,
    -- the shared schema, and downloads/ are routed by the rules above and are
    -- filtered out here so no identifier gets two rules; no research directory
    -- is published wholesale.
    publicFiles <- preprocess publicExperimentFiles
    match (fromList publicFiles) $ do
        route   idRoute
        compile copyFileCompiler

    match "css/*" $ do
        route   idRoute
        compile compressCssCompiler

    match (fromList staticPages) $ do
        route   $ setExtension "html"
        compile $ pandocCompiler
            >>= loadAndApplyTemplate "templates/default.html" baseCtx
            >>= relativizeUrls

    -- Skipped drafts never enter the store, so the listings, feeds, and
    -- sitemap below can use plain 'loadAll' without filtering.
    let publishable metadata = previewDrafts || not (isDraft metadata)
    matchMetadata "posts/*" publishable $ do
        route $ setExtension "html"
        compile $ bibtexMathCompiler cslFile bibFile
            >>= saveSnapshot "content"
            >>= loadAndApplyTemplate "templates/post.html"    postCtx
            >>= loadAndApplyTemplate "templates/default.html" postCtx
            >>= relativizeUrls

    -- One page per multi-post tag (see 'publishedTags'). Page EXISTENCE comes
    -- from buildTags (a rules-level metadata scan), but each page's post list
    -- is drawn from the compiled store and filtered by tag, so a skipped draft
    -- can neither break a tag page's load nor leak into one.
    tags <- buildTags "posts/*" (fromCapture "tags/*.html")

    forM_ (publishedTags tags) $ \(tag, _) ->
      create [fromFilePath ("tags/" ++ slugify tag ++ ".html")] $ do
        route idRoute
        compile $ do
          posts <- recentFirst =<< loadAll "posts/*"
          tagged <- filterM (\p -> elem tag <$> getTags (itemIdentifier p)) posts
          let count = length tagged
              tagCtx =
                  listField "posts" postCtx (return tagged)          <>
                  constField "title" ("Notes tagged #" ++ tag)       <>
                  constField "tag" tag                               <>
                  constField "tagCount"
                    (show count ++ if count == 1 then " note" else " notes") <>
                  baseCtx

          makeItem ""
              >>= loadAndApplyTemplate "templates/tag.html"     tagCtx
              >>= loadAndApplyTemplate "templates/default.html" tagCtx
              >>= relativizeUrls

    forM_ writingPages $ \page -> create [page] $ do
      route idRoute
      compile $ do
        posts <- recentFirst =<< loadAll "posts/*"
        years <- yearGroups posts
        yearItems <- mapM (makeItem . fst) years
        let yearItemCtx =
                field "year" (return . itemBody) <>
                listFieldWith "posts" postCtx (\yearItem ->
                  return (concat [ ps | (y, ps) <- years, y == itemBody yearItem ]))
            archiveCtx =
                listField "years" yearItemCtx (return yearItems) <>
                constField "tagCloud" (tagCloudHtml tags)          <>
                constField "title" "Writing"                       <>
                baseCtx

        makeItem ""
            >>= loadAndApplyTemplate "templates/archive.html" archiveCtx
            >>= loadAndApplyTemplate "templates/default.html" archiveCtx
            >>= relativizeUrls

    match "index.html" $ do
        route idRoute
        compile $ do
            posts <- recentFirst =<< loadAll "posts/*"
            -- The newest post WITH A FIGURE is baked into the featured slot as
            -- the no-JS / first-paint default; js/featured-random.js swaps in a
            -- random figure-having post per visit (see that file). "Latest"
            -- lists every post — the picker hides whichever row is currently
            -- featured to avoid duplication.
            pool <- filterM hasFigure posts
            let featured = take 1 pool
                indexCtx =
                    listField "featured" postCtx (return featured) <>
                    listField "posts"    postCtx (return (take 8 posts)) <>
                    constField "title" "Home"                      <>
                    baseCtx

            getResourceBody
                >>= applyAsTemplate indexCtx
                >>= loadAndApplyTemplate "templates/default.html" indexCtx
                >>= relativizeUrls

    let feedRule name render = create [name] $ do
            route idRoute
            compile $ do
                posts <- fmap (take 20) . recentFirst
                    =<< loadAllSnapshots "posts/*" "content"
                render feedConfiguration feedCtx posts
    feedRule "atom.xml" renderAtom
    feedRule "rss.xml"  renderRss

    -- robots.txt points crawlers here. Absolute URLs are required, so the
    -- entries are not relativized.
    create ["sitemap.xml"] $ do
        route idRoute
        compile $ do
            posts <- recentFirst =<< loadAll "posts/*"
            pages <- loadAll (fromList ("index.html" : writingPages ++ staticPages))
            let entryCtx =
                    constField "root" (feedRoot feedConfiguration) <>
                    dateField "lastmod" "%Y-%m-%d" <>
                    defaultContext
                sitemapCtx :: Context String
                sitemapCtx =
                    listField "entries" entryCtx (return (pages ++ posts))
            makeItem ""
                >>= loadAndApplyTemplate "templates/sitemap.xml" sitemapCtx

    match "404.html" $ do
        route idRoute
        compile copyFileCompiler

    match "robots.txt" $ do
        route idRoute
        compile copyFileCompiler

    match "templates/*" $ compile templateCompiler

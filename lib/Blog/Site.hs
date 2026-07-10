{-# LANGUAGE OverloadedStrings #-}

-- | The Hakyll rule set for the site, assembled from the library's compilers,
-- contexts, and feed configuration.
module Blog.Site
  ( siteRules
  ) where

import Control.Monad (filterM, forM_)
import Hakyll

import Blog.Compilers (bibtexMathCompiler)
import Blog.Context   (baseCtx, postCtx, hasFigure)
import Blog.Feed      (feedConfiguration, feedCtx)

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

    forM_ writingPages $ \page -> create [page] $ do
      route idRoute
      compile $ do
        posts <- recentFirst =<< loadAll "posts/*"
        let archiveCtx =
                listField "posts" postCtx (return posts) <>
                constField "title" "Writing"             <>
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

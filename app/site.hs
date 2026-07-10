-- | Entry point. All rules live in "Blog.Site"; the rest of the build logic
-- (compilers, contexts, feeds, TikZ) lives in the @blog@ library.
--
-- Draft posts (@draft: true@) are excluded from the build unless the
-- @PREVIEW_DRAFTS@ environment variable is set (to anything), e.g.:
--
-- > PREVIEW_DRAFTS=1 stack exec site watch
module Main (main) where

import Data.Maybe (isJust)
import System.Environment (lookupEnv)

import Hakyll (hakyll)

import Blog.Site (siteRules)

main :: IO ()
main = do
  previewDrafts <- isJust <$> lookupEnv "PREVIEW_DRAFTS"
  hakyll (siteRules previewDrafts)

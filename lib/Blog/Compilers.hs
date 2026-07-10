{-# LANGUAGE OverloadedStrings #-}

-- | The post compiler: Pandoc with math, syntax highlighting, BibTeX
-- citations, and the TikZ filter ("Blog.TikZ").
module Blog.Compilers
  ( bibtexMathCompiler
  , wrapTables
  ) where

import Hakyll
import Text.Pandoc.Definition (Block (..))
import Text.Pandoc.Highlighting (pygments)
import Text.Pandoc.Options
import Text.Pandoc.Walk (walk, walkM)

import Blog.TikZ (tikzFilter)

-- | Wrap every table in a @div.table-scroll@ so wide tables scroll within
-- their own frame on narrow viewports instead of overflowing the page. The
-- table keeps its normal full-width layout on desktop; the matching CSS hides
-- the scrollbar.
wrapTables :: Block -> Block
wrapTables t@Table{} = Div ("", ["table-scroll"], []) [t]
wrapTables b         = b

-- | Read a post with citation support, enable the math/raw extensions we rely
-- on, run the TikZ filter, and render with MathJax + pygments highlighting.
bibtexMathCompiler :: String -> String -> Compiler (Item String)
bibtexMathCompiler cslFileName bibFileName = do
  csl <- load $ fromFilePath cslFileName
  bib <- load $ fromFilePath bibFileName

  let mathExtensions =
        [ Ext_tex_math_dollars
        , Ext_tex_math_double_backslash
        , Ext_latex_macros
        , Ext_raw_tex
        , Ext_raw_html
        , Ext_fenced_code_blocks
        , Ext_backtick_code_blocks
        , Ext_fenced_code_attributes
        ]
      defaultExtensions = writerExtensions defaultHakyllWriterOptions
      newExtensions     = foldr enableExtension defaultExtensions mathExtensions
      writerOptions = defaultHakyllWriterOptions
        { writerExtensions     = newExtensions
        , writerHTMLMathMethod = MathJax ""
        , writerHighlightStyle = Just pygments
        }
      readerOptions = defaultHakyllReaderOptions
        { readerExtensions =
            enableExtension Ext_raw_html $
              enableExtension Ext_raw_tex pandocExtensions
        }

  getResourceBody
    >>= readPandocBiblio readerOptions csl bib
    >>= \pandoc -> do
          transformed <- walkM tikzFilter pandoc
          return $ writePandocWith writerOptions (walk wrapTables transformed)

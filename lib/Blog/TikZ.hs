{-# LANGUAGE OverloadedStrings #-}

-- | Render fenced @tikzpicture@ code blocks to inline SVG at build time.
--
-- A Markdown code block tagged @.tikzpicture@ is compiled with @lualatex@
-- (dynamic memory, handles data-heavy diagrams) and converted to SVG with
-- @dvisvgm@ (which preserves transparency, gradients, and PostScript specials
-- that the old @pdf2svg@ path dropped). The SVG is embedded inline so it scales
-- responsively and stays crisp.
--
-- Failure is graceful: a diagram that won't compile is logged to the build and
-- replaced with a visible error box, instead of aborting the whole site build.
-- Posts without any @tikzpicture@ blocks never shell out, so the site builds
-- fine on a machine with no TeX toolchain installed.
--
-- Rendered SVGs are cached on disk under @_cache/tikz@, keyed by a hash of the
-- preamble and diagram source, so editing the prose of a diagram-heavy post
-- does not re-run LaTeX for every unchanged diagram. @site clean@ clears the
-- cache along with the rest of Hakyll's @_cache@.
module Blog.TikZ
  ( tikzFilter
  , renderTikz
  , inlineSvg
  , namespaceIds
  ) where

import Data.Char (ord)
import Data.List (foldl', isInfixOf)
import qualified Data.Text as T
import qualified Data.Text.IO as TIO
import Hakyll (Compiler, unsafeCompiler)
import Text.Pandoc.Definition (Block (..), Format (..))
import System.Directory (createDirectoryIfMissing, doesFileExist)
import System.Exit (ExitCode (..))
import System.IO (hPutStrLn, stderr)
import System.IO.Temp (withSystemTempDirectory)
import System.Process (readProcessWithExitCode)

-- | Pandoc filter: replace @.tikzpicture@ code blocks with rendered inline SVG,
-- leaving every other block untouched.
tikzFilter :: Block -> Compiler Block
tikzFilter (CodeBlock (_, classes, _) contents)
  | "tikzpicture" `elem` classes = do
      result <- unsafeCompiler $ renderTikz (T.unpack contents)
      let html = case result of
            Right svg -> "<div class=\"tikz-figure\">" ++ inlineSvg svg ++ "</div>"
            Left err  -> "<div class=\"tikz-error\"><strong>Diagram failed to render.</strong>"
                          ++ "<pre>" ++ escapeHtml err ++ "</pre></div>"
      return $ RawBlock (Format "html") (T.pack html)
tikzFilter block = return block

-- | Drop the XML prolog / DOCTYPE that @dvisvgm@ emits, returning the markup
-- from the opening @\<svg@ tag onward so it is safe to inline in HTML. Pure,
-- so it is unit-testable.
inlineSvg :: String -> String
inlineSvg svg =
  let (_, rest) = T.breakOn "<svg" (T.pack svg)
  in if T.null rest then svg else T.unpack rest

-- | dvisvgm reuses glyph paths via @id@/@\<use\>@ with names like @g3-66@, and
-- restarts that numbering for every file. Inlining several such SVGs in one HTML
-- page makes those ids collide, so a later diagram's glyphs get drawn with an
-- earlier diagram's paths (an "R" comes out as a "C"). Prefixing every id and
-- every internal reference with a per-diagram token makes them page-unique.
-- Pure, so it is unit-testable.
namespaceIds :: T.Text -> T.Text -> T.Text
namespaceIds prefix =
    rep "id=\""    ("id=\"" <> prefix)
  . rep "id='"     ("id='" <> prefix)
  . rep "href=\"#" ("href=\"#" <> prefix)
  . rep "href='#"  ("href='#" <> prefix)
  . rep "url(#"    ("url(#" <> prefix)
  where rep = T.replace

-- | A deterministic, page-unique, valid-identifier prefix derived from the
-- diagram source (djb2). Stable across builds so output stays reproducible.
idPrefix :: String -> T.Text
idPrefix s = T.pack ('n' : show (foldl' step (5381 :: Integer) s))
  where step acc c = (acc * 33 + fromIntegral (ord c)) `mod` 1000000007

-- | Minimal HTML escaping for the error box.
escapeHtml :: String -> String
escapeHtml = concatMap esc
  where
    esc '&' = "&amp;"
    esc '<' = "&lt;"
    esc '>' = "&gt;"
    esc c   = [c]

-- | LaTeX preamble wrapped around each @tikzpicture@ snippet.
tikzPreamble :: String
tikzPreamble = unlines
  [ "\\documentclass[crop,tikz,border=4pt]{standalone}"
  , "\\usepackage{tikz}"
  , "\\usepackage{pgfplots}"
  , "\\usepackage{amsmath}"
  , "\\usepackage[version=4]{mhchem}"
  , "\\usepackage[american]{circuitikz}"
  -- @standalone@'s auto-crop only knows @tikzpicture@; register @circuitikz@ too
  -- so schematics crop to the drawing instead of a full page.
  , "\\standaloneenv{circuitikz}"
  , "\\pgfplotsset{compat=1.18}"
  , "\\usepgfplotslibrary{units}"
  , "\\usetikzlibrary{arrows.meta}"
  , "\\usetikzlibrary{patterns,patterns.meta}"
  , "\\usetikzlibrary{backgrounds}"
  , "\\usetikzlibrary{calc}"
  , "\\usetikzlibrary{decorations.pathmorphing}"
  , "\\usetikzlibrary{decorations.markings}"
  , "\\usetikzlibrary{matrix,arrows}"
  , "\\begin{document}"
  ]

-- | Where successfully rendered diagrams are cached between builds. Lives
-- inside Hakyll's cache directory so @site clean@ wipes it too.
tikzCacheDir :: FilePath
tikzCacheDir = "_cache/tikz"

-- | Render a @tikzpicture@ body to SVG, going to the on-disk cache first.
-- The key hashes the preamble as well as the diagram source, so changing
-- 'tikzPreamble' invalidates every cached diagram. Only successful renders
-- are cached; failures re-run so a fixed toolchain is picked up.
renderTikz :: String -> IO (Either String String)
renderTikz tikzCode = do
  let cacheFile = tikzCacheDir ++ "/"
        ++ T.unpack (idPrefix (tikzPreamble ++ tikzCode)) ++ ".svg"
  cached <- doesFileExist cacheFile
  if cached
    then Right . T.unpack <$> TIO.readFile cacheFile
    else do
      result <- compileTikz tikzCode
      case result of
        Right svg -> do
          createDirectoryIfMissing True tikzCacheDir
          TIO.writeFile cacheFile (T.pack svg)
        Left _ -> return ()
      return result

-- | Compile a @tikzpicture@ body to SVG via @lualatex@ + @dvisvgm@ in a temp
-- dir. Returns @Left@ with a diagnostic on failure (build continues).
compileTikz :: String -> IO (Either String String)
compileTikz tikzCode = withSystemTempDirectory "blog-tikz" $ \dir -> do
  let texFile = dir ++ "/tikz.tex"
      pdfFile = dir ++ "/tikz.pdf"
      svgFile = dir ++ "/tikz.svg"

  -- Blocks that already open their own picture environment (@tikzpicture@, so
  -- they can pass options like a 3D basis, or @circuitikz@ for schematics) are
  -- used verbatim; otherwise the block is the picture body and we wrap it (the
  -- established convention — e.g. a bare pgfplots @axis@).
  let opensOwnPicture =
        any (`isInfixOf` tikzCode) ["\\begin{tikzpicture}", "\\begin{circuitikz}"]
      body
        | opensOwnPicture = tikzCode
        | otherwise = "\\begin{tikzpicture}\n" ++ tikzCode ++ "\n\\end{tikzpicture}"
  writeFile texFile $ tikzPreamble ++ body ++ "\n\\end{document}\n"

  (texCode, texOut, texErr) <- readProcessWithExitCode "lualatex"
    ["-halt-on-error", "-interaction=nonstopmode", "-output-directory=" ++ dir, texFile]
    ""
  case texCode of
    ExitFailure _ -> bail "lualatex" (texOut ++ texErr)
    ExitSuccess -> do
      (svgCode, svgOut, svgErr) <- readProcessWithExitCode "dvisvgm"
        ["--pdf", "--no-fonts", "--output=" ++ svgFile, pdfFile]
        ""
      case svgCode of
        ExitFailure _ -> bail "dvisvgm" (svgOut ++ svgErr)
        ExitSuccess -> do
          svg <- TIO.readFile svgFile          -- strict read before temp dir is cleaned
          return $! Right (T.unpack (namespaceIds (idPrefix tikzCode) svg))
  where
    bail tool msg = do
      hPutStrLn stderr $ "[tikz] " ++ tool ++ " failed:\n" ++ msg
      return $ Left (tool ++ " failed (see build log)")

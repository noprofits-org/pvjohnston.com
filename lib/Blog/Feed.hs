{-# LANGUAGE OverloadedStrings #-}

-- | Atom/RSS feed configuration and the context the feeds render with.
module Blog.Feed
  ( feedConfiguration
  , feedCtx
  ) where

import Hakyll

import Blog.Context (postCtx)

-- | Shared configuration for both the Atom and RSS feeds.
feedConfiguration :: FeedConfiguration
feedConfiguration = FeedConfiguration
  { feedTitle       = "Peter Johnston — Notes"
  , feedDescription = "Science, AI-assisted tools, automation, art, and other things worth understanding."
  , feedAuthorName  = "Peter Johnston"
  , feedAuthorEmail = "pvjohnst@gmail.com"
  , feedRoot        = "https://pvjohnston.com"
  }

-- | Feed entries need a @description@ field, mapped to the post body snapshot.
feedCtx :: Context String
feedCtx = postCtx <> bodyField "description"

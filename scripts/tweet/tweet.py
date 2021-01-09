#!/usr/bin/env python
# coding: utf-8

import argparse
import twitter

parser = argparse.ArgumentParser(description='Credenciales y contenido del tweet')

parser.add_argument('consumer_key', type=str)
parser.add_argument('consumer_secret', type=str)
parser.add_argument('access_token_key', type=str)
parser.add_argument('access_token_secret', type=str)
parser.add_argument('tweet_text', type=str)
parser.add_argument('tweet_media_location', type=str)

args = parser.parse_args()

api = twitter.Api(consumer_key=args.consumer_key,
                  consumer_secret=args.consumer_secret,
                  access_token_key=args.access_token_key,
                  access_token_secret=args.access_token_secret)

api.PostUpdate(args.tweet_text, media=args.tweet_media_location)
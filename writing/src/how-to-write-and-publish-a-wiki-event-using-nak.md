---
title: How to Write and Publish a Wiki Event using Nak
date: 2025-04-04
summary: Short tutorial explaining how to publish wiki articles via the command line tool nak
slug: how-to-write-and-publish-a-wiki-event-using-nak
tags: wiki, documentation, nak
headerImage: assets/writing/how-to-write-and-publish-a-wiki-event-using-nak-header.webp
nostrEvent: 3e7580a2946e21a840d21ef5891329b6a46cae3b2d04b7098d5a2e13564c1eb9
nostrDtag: 1743798227950
nostrRelays: wss://nostr.wine, wss://nostr.mom, wss://relay.ditto.pub, wss://nostr.oxtr.dev, wss://nostr-01.yakihonne.com
---
I'm making this tutorial for myself, as I plan to write many wiki pages describing DVM kinds, as a resource for DVMDash. 

Wiki pages on Nostr are written using AsciiDoc. If you don't know ascii doc, get an LLM (like https://duck.ai) to help you format into the right syntax.

Here's the test wiki page I'm going to write:


```
= Simple AsciiDoc Demo

This is a simple demonstration of AsciiDoc syntax for testing purposes. 

== Features

AsciiDoc offers many formatting options that are easy to use. 

* Easy to learn 
* Supports rich text formatting 
* Can include code snippets 
* Works great for documentation 

[source,json] 
---- 
{ "name": "Test", "version": "1.0", "active": true } 
----
```

# We're going to use nak to publish it


First, install `nak` if you haven't already

```
go install github.com/fiatjaf/nak@latest
```

*Note: if you don't use Go a lot, you may need to first install it and then add it to your path so the `nak` command is recognized by the terminal*


```
# this is how to add it to your path on mac if using zsh
echo 'export PATH=$PATH:$(go env GOPATH)/bin' >> ~/.zshrc
```

And here's how to sign and publish this event with nak.

*First, if you want to use your own nostr sec key, you can set the env variable to it and nak will use that if no secret key is specified*

```
# replace with your full secret key
export NOSTR_SECRET_KEY="nsec1zcdn..."
```

Now to sign and publish the event:

*Note: inner double quotes need to be escaped with a `\` before them in order to keep the formatting correct, because we're doing this in the terminal*

```
nak event -k 30818 -d "dvm-wiki-page-test" -t 'title=dvm wiki page test'  -c "= Simple AsciiDoc Demo\n\nThis is a simple demonstration of AsciiDoc syntax for testing purposes. \n\n== Features\n\nAsciiDoc offers many formatting options that are easy to use. \n\n* Easy to learn \n* Supports rich text formatting \n* Can include code snippets \n* Works great for documentation \n\n[source,json] \n---- \n{ \"name\": \"Test\", \"version\": \"1.0\", \"active\": true } \n----" wss://relay.primal.net wss://relay.damus.io wss://relay.wikifreedia.xyz
```

You've now published your first wiki page! If done correctly, it will show up on wikistr.com, like mine did here: https://wikistr.com/dvm-wiki-page-test*da18e9860040f3bf493876fc16b1a912ae5a6f6fa8d5159c3de2b8233a0d9851 

and on wikifreedia.xyz https://wikifreedia.xyz/dvm-wiki-page-test/dustind@dtdannen.github.io

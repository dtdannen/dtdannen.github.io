---
title: Post DVM Drama
date: 2025-08-01
summary: What started as a controversial 'reset the spec' PR turned into productive community collaboration. This article chronicles the DVM discussions and my take on where we should go: one event kind for everything, better relay compatibility, and cleaner patterns. See how disagreement led to innovative thinking about Nostr's API ecosystem.
slug: post-dvm-drama
tags: nostr, data vending machine, ai, api, contextvm
headerImage: assets/writing/post-dvm-drama-header.webp
nostrEvent: cd9c8fe3a82bac1cf990f8341f503f9f70e9cf363d028527fc4837ef13991365
nostrDtag: 1754020882194
nostrRelays: wss://nostr.wine, wss://nostr.mom, wss://relay.ditto.pub, wss://nostr.oxtr.dev, wss://nostr-01.yakihonne.com
---
May and June were pretty heated months for Data Vending Machines. We've been hashing things out over on the NIPs repo via Github PRs. It started with [PR 1903](https://github.com/nostr-protocol/nips/pull/1903) when [npub180cvv07tjdrrg…yjh6w6](https://njump.me/npub180cvv07tjdrrgpa0j7j7tmnyl2yr6yr7l8j4s3evf6u64th6gkwsyjh6w6) recommended resetting the spec and starting over, which then caused rebuttal PRs from myself and others: see [PR 1941](https://github.com/nostr-protocol/nips/pull/1941), [PR 1942](https://github.com/nostr-protocol/nips/pull/1942), and even [PR 1929](https://github.com/nostr-protocol/nips/pull/1929). When the dust settled, there were a few things everyone seemed to agree on, and then there were unresolved disagreements that aren't really a big deal. In the last few weeks, there's been some innovative ideas from [npub1gzuushllat7pe…3ea5ds](https://njump.me/npub1gzuushllat7pet0ccv9yuhygvc8ldeyhrgxuwg744dn5khnpk3gs3ea5ds) that I'm going to include as well. I'll present as much as I can here, because now that things have settled down, folks still want to build DVMs, and there's new thinking on what the best way to do it is. This article is my perspective on how you should build your next DVM.

## But what is a DVM?

DVMs are APIs on Nostr - [go read this if you want to know more](https://habla.news/u/dustind@dtdannen.github.io/1751579151592). The greatest innovation of DVMs is that you can offer a (free or paid) service **without** needing a domain name or IP address.  

## Why am I writing this?

A few of us got together in late May to respond to [npub180cvv07tjdrrg…yjh6w6](https://njump.me/npub180cvv07tjdrrgpa0j7j7tmnyl2yr6yr7l8j4s3evf6u64th6gkwsyjh6w6)'s PR to "reset the DVM spec" and after weeks of discussions and iterations, finally landed on what most of us felt was a complete and comprehensive guide to a spec for DVMs. It's too long for this article, if you look at the new [nip-90.md file](https://github.com/nostr-protocol/nips/blob/8b254339003f1d6784c505d9d118184c34d36cbc/90.md) under PR 1941, you can see the whole thing. We have spent a long time debating and discussing nuances of DVMs, and this article is my attempt to summarize what we agree on and what new, modern DVMs should look like. While a new DVM spec **has not yet been merged into the NIPs repo**, there is strong support that the spec should be less descriptive, and therefore much shorter than what we had written in PR 1941; more like what PR 1942 proposes. I'm fine with that, but most people who actually want to build DVMs are going to have a lot of choices to make, and a less descriptive spec only makes that harder. The answer to those choices has become clearer, especially with recent innovative thinking from [npub1gzuushllat7pe…3ea5ds](https://njump.me/npub1gzuushllat7pet0ccv9yuhygvc8ldeyhrgxuwg744dn5khnpk3gs3ea5ds) with his work on [npub1dvmcpmefwtnn6…w33jdm](https://njump.me/npub1dvmcpmefwtnn6dctsj3728n64xhrf06p9yude77echmrkgs5zmyqw33jdm). 

If you are considering building tools that AI agents can use, you should absolutely make a ContextVM (formerly DVMCP) instead of a DVM. You could actually do almost any DVM as a ContextVM, but ContextVM adds some overhead and therefore I still think DVMs have their own place in offering computational services over Nostr. It may be better to think of DVMs as a design pattern rather than a hard spec; for a practical guide to what decisions to make to launch your first DVM, see [this new article that covers every step to build new DVMs along with full examples](https://habla.news/u/dustind@dtdannen.github.io/1754018912170).

## What we all seem to agree on...

### We agree NIP-89 shouldn't be used for DVM Announcements

[NIP-89](https://github.com/nostr-protocol/nips/blob/0595d438aaa163dd33ed00748026698a411a0861/89.md) confused so many people! If you don't know what NIP-89 is, it's a fancy way of using Nostr events to tell clients what other clients could open any kind of note. So if you have a special wiki client that can open wiki notes (kind 30818), you can publish a NIP-89 announcement (kind 31990) saying your app at url X can open kind 30818, and then if a note shows up in someone else's app, they can tell their user "Hey while my client that you're using right now can't show a kind 30818 note, you can go use client X to show it nicely".

The original DVM spec, [NIP-90](https://github.com/nostr-protocol/nips/blob/0595d438aaa163dd33ed00748026698a411a0861/90.md), referenced NIP-89 as the way to announce DVMs. After all, DVMs are kind of like clients for job request kinds. Most DVMs only support a single Job Request Kind (like algorithmic feed DVMs respond to job request kind 5300). The problem is that DVMs are actually pretty different than software clients that display notes for humans to use. In this way, DVMs are more like workers, not clients, and it doesn't make sense to go tell a human to use a DVM to consume a job request kind 5300. 

So the new recommendation is to use a different, non NIP-89 kind for DVM announcements, that is specifically for DVM announcements and DVM announcements ONLY. We saw kind 31999 wasn't being used by anyone else and for a while that was the leading favorite; however in aim of making the common DVM design pattern as simple as possible, it's better to use kind 11999 instead. The reason is that it's simpler if every DVM has its own npub (this was highly debated since it makes life harder for someone running multiple DVMs under a brand). If every DVM has its own npub, then using kind 11999 is possible and querying relays for the DVM announcement is simpler (you just query for the dvm's pubkey and kind 11999). The alternative was this messy business with `d` tags, where multiple DVMs could exist under a single npub, where each DVM has it's own `d` tag, and if each of those DVMs had their own announcements, you would have to use addressable events in the kind 3xxxx range.

**Takeaway:** Use kind 11999 to announce your DVM; each DVM must have it's own npub.

### We agree kinds 5000-7000 are too limiting for DVMs

We all knew eventually DVMs would be so popular, that having to use kinds 5000-7000 would only go on for so long (you literally are restricted to 1000 job request kind numbers ONLY, which seems a very small number) - this is like saying there could only have been 1000 kinds of DVMs. We know there are way more than 1000 kinds of APIs in the world, so expecting 1000 to be enough isn't realistic. 

There was a lot of debate about with what to replace this kind range with. If you're not familiar, kinds 5000-5999 were job request types (like 5100 is an AI image generation task and 5300 is a request for an algorithmically generated feed). Then kinds 6000-6999 were job response kinds. So if you ask for an image to be generated via a 5100 request, the resulting image would be sent back to you as a 6100 event (the job result kind is always 1000 + the job request kind).

So what about kind 7000? This was an intermediate event used for everything from letting a user know the job started processing, requesting payment, reporting an error had occurred, or anything else you could imagine!

One major problem with these event kinds is that they do not fall in the ephemeral range (kinds 20000-29999) and so relays by default expect that they should hold on to these events as long as possible (sorry [npub18kzz4lkdtc5n7…0mx5sz](https://njump.me/npub18kzz4lkdtc5n729kvfunxuz287uvu9f64ywhjz43ra482t2y5sks0mx5sz)). This causes a big headache for relay operators. Once a DVM job is finished, none of the events are needed anymore for any of the parties involved, so in most cases they are really of an ephemeral nature and can be discarded. We'll get to it later, but for most common DVM use cases, your job request event SHOULD be an ephemeral event, so that relays can delete it once the job is finished or after a certain time period.

**Takeaway:** Use an ephemeral kind number for job events. If you need an intermediate or error status event, don't use kind 7000, just use the same job request kind (more on this below).

### We agree heartbeat events might be useful

Both PRs 1941 and 1942 include heartbeat events. A heartbeat event is useful to let people know your service is online and available when there may not be other data to indicate that it is. This is especially useful if all or part of the DVM interaction is hidden / encrypted such as via NIP-44 gift wraps (like what [npub1dvmcpmefwtnn6…w33jdm](https://njump.me/npub1dvmcpmefwtnn6dctsj3728n64xhrf06p9yude77echmrkgs5zmyqw33jdm) does).

### What these agreements really mean...

First, as long as we all agree that a specific kind number (like 11999) is what should be used to announce a DVM, then we can keep the overall DVM ecosystem! Sites like [stats.dvmdash.live](https://stats.dvmdash.live/), [noogle.lol](https://noogle.lol/nip89), and [nostrhub.io](https://nostrhub.io/dvm) can all easily show users the current DVM offerings by regularly querying relays for kind 11999 announcements.

Second, it means that the event kinds that DVMs can use to operate.... is practically infinite. No longer are DVMs confined to a 5xxx job request kind and a corresponding 6xxx job result kind, and 7000 kind status updates. The end result is that the spec is reduced... and it gives more freedom to devs (overall a great thing), but since so many DVMs seemed to follow a similar pattern before; I believe we still need a common design pattern for DVMs, even if it's not in the spec. However, don't go choosing your own event kind just yet....

## Innovative Ideas from Gzuuus

[npub1gzuushllat7pe…3ea5ds](https://njump.me/npub1gzuushllat7pet0ccv9yuhygvc8ldeyhrgxuwg744dn5khnpk3gs3ea5ds) who's working on ContextVM has suggested some of the best innovative ideas for the next version of DVMs. 

**Use same kind for responses and requests:** Original DVMs had request events in the range 5000-5999 and a corresponding response would be an event with a kind +1000, so a request for an algorithm feed is a kind 5300 and the response containing the notes is a kind 6300. We don't actually need to do this.... You can just use kind 5300 for both. Responses are identified by the fact that they are tagging the original request event id AND they are coming from a different pubkey (the DVM provider). When the client is subscribing to the relay, they just need to add a filter to know whether an event is a response.

**Use the same kind for ALL DVMs:** This one is a little crazy. What if we don't even need a separate kind per each DVM category? We've seen over 30 different kinds of DVM jobs over the last 2 years (see https://stats.dvmdash.live/kind-stats for current ones; some aren't used anymore). We could simply have a single kind, like kind **25000** for every DVM. The only reason to have different kinds was to support open-ended requests and treat different kinds like different types of jobs. Like if there are multiple AI image generators running on kind 5100 and I want to get the cheapest one, I can submit a generic kind 5100 request without specifying a provider, then wait for online providers to respond with prices, and then I can choose the one I want. 

But this isn't really how any existing API's work on the internet. Every service provider has their own documentation, own process, own reputation and realistically, most people want to pick a provider that they can rely on and build with that. While the free market idea of DVMs competing for business is ideal, there are many things that make this hard in practice or to reliably build these dynamics into apps. 

There's a lot of overhead to having infinite kind numbers for DVMs, let alone even just a thousand per the original spec. Most relays don't want you querying for thousands of event kinds (I know; DVMDash stats dashboard does this and it was a headache to get events from relays because relays expect you to query for a relatively small number of kinds at a time).

Instead, we could just pick a new tag called `category` and let clients put anything they want in it. Kind 5300 DVMs could switch to kind 25000 and add a `category` tag with the value **algorithmic feed**. Existing clients can query all DVM announcements that have this tag value when customers want to choose between feed generators. This makes relay interactions cleaner, and lets DVMs categorize themselves with alphanumeric strings rather than just integers for kind numbers. It would be easier to know what categories of DVMs exist without having to go read their documentation.

### A scheme for encryption

DVMs should offer end-to-end encryption using a simplified version of NIP-17/NIP-59, just like how ContextVM does it. With this encryption mechanism, most of the DVM communication cannot be seen by external parties, and therefore it also reduces the ability of DVMDash to provide stats on DVM usage; which is ultimately better for end users and service providers. However, because of this, heartbeat events become even more important so that DVMs can let people know they are online and operational (if all DVM events can be seen, we can use those to determine if a DVM is online and how recently it responded; but this encryption scheme removes this capability).

**Note:** While encryption is an important part of the future of DVMs, the core protocol improvements discussed in this article can be implemented without encryption. A detailed implementation guide for encrypted DVMs is coming soon. For now, developers can start building with the simplified event kinds and patterns described here.

## Okay, so what should the new event kinds be?

| Kind  | Description                           |
| ----- | ------------------------------------- |
| 11999 | DVM Announcement Event (Replaceable)  |
| 25000 | DVM Request/Responses (Ephemeral)     |
| 11998 | DVM Heartbeat Events (Replaceable)    |


That's it! Do you want to offer an API over Nostr? Check out [this new guide on every step needed to build DVMs](https://habla.news/u/dustind@dtdannen.github.io/1754018912170) with these improvements.

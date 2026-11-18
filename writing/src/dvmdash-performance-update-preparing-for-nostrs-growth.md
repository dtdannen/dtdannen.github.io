---
title: DVMDash Performance Update: Preparing for Nostr's Growth
date: 2025-01-22
summary: Redesigned from the ground up, DVMDash will feature horizontal scaling that can process millions of DVM events per day, ensuring it's ready to grow alongside Nostr's expanding DVM ecosystem.
slug: dvmdash-performance-update-preparing-for-nostrs-growth
tags: dvm, rundvm, nip90, ai, dvmdash, opensats
headerImage: assets/writing/dvmdash-performance-update-preparing-for-nostrs-growth-header.webp
nostrEvent: 34fc0cbeaed443de54f47b0f7a24f98a1d6b57251528f6d633ec171bf2217378
nostrDtag: 1737576026224
nostrRelays: wss://nostr.wine, wss://nostr.mom, wss://relay.ditto.pub, wss://nostr.oxtr.dev, wss://nostr-01.yakihonne.com
---
Since DVMs were introduced to Nostr in July 2023, we've witnessed remarkable growth - over 2.5 million DVM events (Kinds 5000-7000) and counting. Last fall, when Primal added custom feeds (Kind 5300 DVMs), we saw a 10x surge in DVM activity. To handle this growth, I've spent the last few months completely rewriting DVMDash.

The first version of DVMDash, still live at [https://dvmdash.live](https://dvmdash.live), unfortunately uses full database table scans to compute the metrics. The code was simpler, but the computation ran on the database. This meant the only way to scale the system was to upgrade the database. Using managed databases (like AWS, Azure, Digital Ocean) beyond the lower tiers gets expensive quickly. 

The other problem with the first version: it computes metrics globally (well... as global as you can get; there's no true global with Nostr). Global or all-time metrics aren't sustainable with a system that plans to analyze billions of events in the future (a long term goal for DVMDash). Especially metrics like the number of unique DVMs, Kinds, and Users. I spent more time than I care to admit on possible designs, and have settled on these design principles for now:

1. Precise accurate metrics will only be computed for the last 30 days of DVM activity. 
2. At the turn of a new month, we will compute a snapshot of the last month's activity, and a snapshot per DVM and per Kind, and store them in a historical table. This way we can see what any given month in the past looked like from a bird's eye view with metrics like number of job requests, job results, a count of unique DVMs, kinds and users, which DVMs ran jobs on which kinds, etc. The monthly data will all be aggregate. 

The goal of the new redesign is to support processing millions of DVM events an hour. Therefore we need to ensure we can horizontally scale the processing as the traffic increases. Horizontal scaling was the primary goal of this new redesign, and early results indicate it's working. 

The new architecture for DVMDash uses a redis queue to hold events collected from relays. Then batches of events are pulled off of the queue by dvm event analyzers to compute metrics. Duplicating these analyzers is one way DVMDash can horizontally scale. 

To see if increasing the number of dvm event analyzers improves speed, I ran a performance test on Digital Ocean using real DVM events collected from Jan. 1st 2024 to Jan 9th 2025, which includes more than 2.4 million events. The only difference between each run is the number of DVM event analyzers ranging from 1 to 6. 

![cumulative dvm events performance results 01212025](assets/writing/dvmdash-performance-update-preparing-for-nostrs-growth-figure-8797.webp)

The first graph shows that adding more event analyzers has a significant speed improvement. With only one analyzer it took nearly an hour to process the 2.4 million events. With every added analyzer, there was a noticeable speedup, as can be seen in the graph. With n=6 analyzers, we were able to process all 2.4 million events in about 10 minutes. 

When we look at the rate of processing shown in the second graph, we can see that we get up to 300k dvm events processed per minute when n=6, compared to just ~50k events processed when n=1.

![analyzer rates performance results 01212025](assets/writing/dvmdash-performance-update-preparing-for-nostrs-growth-figure-3071.webp)

While I did test beyond 6 analyzers, I found the sweet spot for the current infrastructure setup to be around 6 analyzers. This provides plenty of headroom above our current processing needs, which typically see less than a million events per month. Even at a million DVM events per day, DVMDash should be able to handle it with n=2 analyzers running. The most important takeaway is that DVMDash can now horizontally scale by adding more analyzers as DVM activity grows in the future.

The code to run these performance tests, either locally or on Digital Ocean (you'd need an API key), is in the dvmdash repo, so anyone can replicate these tests. There's a lot of nuance to scaling that I'm leaving out of this short article, and you can't get away from having to adjust database capacity (especially number of connections). The code for this test can be found in `experiments/test_batch_processing_scaling.py` and the code to produce the graphs is in `experiments/graph_batch_processing_scaling_data.py`. For now this is still in the `full-redesign` branch, soon it will be merged into `main`.

The live version of dvmdash doesn't have these performance updates yet, a complete redesign is coming soon, including a new UI.

I've had my head down working on this rewrite, and couldn't move on to add new features until this was done. Thank you to the folks who made github issues, I'll be getting to those soon.

DVMDash is open source, please drop by and give us a feature request, bug report, pull request or star. Thanks to OpenSats for funding this work.

Github: [https://github.com/dtdannen/dvmdash](https://github.com/dtdannen/dvmdash)

Shoutout to [npub12xeqxplp5ut4h…nzrk5w](https://njump.me/npub12xeqxplp5ut4h92s3vxthrdv30j0czxz9a8tef8cfg2cs59r85gqnzrk5w) for helping me think through database design choices.

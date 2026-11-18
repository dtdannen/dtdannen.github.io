---
title: Announcing DVMDash v0.1
date: 2024-08-14
summary: This article announces the first version of DVMDash, a monitoring and debugging tool for Data Vending Machine activity on Nostr.
slug: announcing-dvmdash-v0-1
tags: dvm, ai, nostr
headerImage: assets/writing/announcing-dvmdash-v0-1-header.webp
nostrEvent: dbb5b25b80fbf82f689b8479f63d6cec4cb1570f3944c1fb03175d1d23ed0012
nostrDtag: 1723526541960
nostrRelays: wss://nostr.wine, wss://nostr.mom, wss://relay.ditto.pub, wss://nostr.oxtr.dev, wss://nostr-01.yakihonne.com
---
After months of development I am excited to officially announce the first version of DVMDash (v0.1). DVMDash is a monitoring and debugging tool for all Data Vending Machine (DVM) activity on Nostr. The website is live at [https://dvmdash.live](https://dvmdash.live) and the code is available on [Github](https://github.com/dtdannen/dvmdash).

Data Vending Machines ([NIP-90](https://github.com/nostr-protocol/nips/blob/master/90.md)) offload computationally expensive tasks from relays and clients in a decentralized, free-market manner. They are especially useful for AI tools, algorithmic processing of user’s feeds, and many other use cases.  

The long term goal of DVMDash is to become 1) a place to easily see what’s happening in the DVM ecosystem with metrics and graphs, and  2) provide real-time tools to help developers monitor, debug, and improve their DVMs.

DVMDash aims to enable users to answer these types of questions at a glance:
* What’s the most popular DVM right now?
* How much money is being paid to image generation DVMs?
* Is any DVM down at the moment? When was the last time that DVM completed a task?
* Have any DVMs failed to deliver after accepting payment? Did they refund that payment?
* How long does it take this DVM to respond?
* For task X, what’s the average amount of time it takes for a DVM to complete the task?
* … and more

For developers working with DVMs there is now a visual, graph based tool that shows DVM-chain activity. DVMs have already started calling other DVMs to assist with work. Soon, we will have humans in the loop monitoring DVM activity, or completing tasks themselves. The activity trace of which DVM is being called as part of a sub-task from another DVM will become complicated, especially because these decisions will be made at run-time and are not known ahead of time. Building a tool to help users and developers understand where a DVM is in this activity trace, whether it’s gotten stuck or is just taking a long time, will be invaluable. *For now, the website only shows 1 step of a dvm chain from a user's request.*

One of the main designs for the site is that it is highly _clickable_, meaning whenever you see a DVM, Kind, User, or Event ID, you can click it and open that up in a new page to inspect it.

Another aspect of this website is that it should be fast. If you submit a DVM request, you should see it in DVMDash within seconds, as well as events from DVMs interacting with your request. I have attempted to obtain DVM events from relays as quickly as possible and compute metrics over them within seconds. 

This project makes use of a nosql database and graph database, currently set to use mongo db and neo4j, for which there are free, community versions that can be run locally.

Finally, I’m grateful to [npub10pensatlcfwkt…yfn34f](https://njump.me/npub10pensatlcfwktnvjjw2dtem38n6rvw8g6fv73h84cuacxn4c28eqyfn34f) for supporting this project.

## Features in v0.1:

### Global Network Metrics:

This page shows the following metrics:
- **DVM Requests:** Number of unencrypted DVM requests (kind 5000-5999)
- **DVM Results:** Number of unencrypted DVM results (kind 6000-6999)
- **DVM Request Kinds Seen:** Number of unique kinds in the Kind range 5000-5999 (except for known non-DVM kinds 5666 and 5969)
- **DVM Result Kinds Seen:** Number of unique kinds in the Kind range 6000-6999 (except for known non-DVM kinds 6666 and 6969)
- **DVM Pub Keys Seen:** Number of unique pub keys that have written a kind 6000-6999 (except for known non-DVM kinds) or have published a kind 31990 event that specifies a ‘k’ tag value between 5000-5999
- **DVM Profiles (NIP-89) Seen**: Number of 31990 that have a ‘k’ tag value for kind 5000-5999
- **Most Popular DVM**: The DVM that has produced the most result events (kind 6000-6999)
- **Most Popular Kind**: The Kind in range 5000-5999 that has the most requests by users.
- **24 hr DVM Requests**: Number of kind 5000-5999 events created in the last 24 hrs
- **24 hr DVM Results**: Number of kind 6000-6999 events created in the last 24 hours
- **1 week DVM Requests**: Number of kind 5000-5999 events created in the last week
- **1 week DVM Results**: Number of kind 6000-6999 events created in the last week
- **Unique Users of DVMs**: Number of unique pubkeys of kind 5000-5999 events
- **Total Sats Paid to DVMs**: 
  - This is an estimate.
  - This value is likely a lower bound as it does not take into consideration subscriptions paid to DVMs
  - This is calculated by counting the values of all invoices where:
    - A DVM published a kind 7000 event requesting payment and containing an invoice
    - The DVM later provided a DVM Result for the same job for which it requested payment.
    - The assumption is that the invoice was paid, otherwise the DVM would not have done the work
  - Note that because there are multiple ways to pay a DVM such as lightning invoices, ecash, and subscriptions, there is no guaranteed way to know whether a DVM has been paid. Additionally, there is no way to know that a DVM completed the job because some DVMs may not publish a final result event and instead send the user a DM or take some other kind of action.


### Recent Requests:
This page shows the most recent 3 events per kind, sorted by created date. You should always be able to find the last 3 events here of all DVM kinds.

### DVM Browser:
This page will either show a profile of a specific DVM, or when no DVM is given in the url, it will show a table of all DVMs with some high level stats. Users can click on a DVM in the table to load the DVM specific page.

### Kind Browser:
This page will either show data on a specific kind including all DVMs that have performed jobs of that kind, or when no kind is given, it will show a table summarizing activity across all Kinds.

### Debug:
This page shows the graph based visualization of all events, users, and DVMs involved in a single job as well as a table of all events in order from oldest to newest. When no event is given, this page shows the 200 most recent events where the user can click on an event in order to debug that job. The graph-based visualization allows the user to zoom in and out and move around the graph, as well as double click on any node in the graph (except invoices) to open up that event, user, or dvm in a new page. 

### Playground:
This page is currently under development and may not work at the moment. If it does work, in the current state you can login with NIP-07 extension and broadcast a 5050 event with some text and then the page will show you events from DVMs. This page will be used to interact with DVMs live. A current good alternative to this feature, for some but not all kinds, is [https://vendata.io/](https://vendata.io/).

## Looking to the Future

I originally built DVMDash out of Fear-of-Missing-Out (FOMO); I wanted to make AI systems that were comprised of DVMs but my day job was taking up a lot of my time. I needed to know when someone was performing a new task or launching a new AI or Nostr tool!

I have a long list of DVMs and Agents I hope to build and I needed DVMDash to help me do it; I hope it helps you achieve your goals with Nostr, DVMs, and even AI. To this end, I wish for this tool to be useful to others, so if you would like a feature, please [submit a git issue here](https://github.com/dtdannen/dvmdash/issues/new) or _note_ me on Nostr!

### Immediate Next Steps:
- Refactoring code and removing code that is no longer used
- Improve documentation to run the project locally
- Adding a metric for number of encrypted requests
- Adding a metric for number of encrypted results


### Long Term Goals:
- Add more metrics based on community feedback
- Add plots showing metrics over time
- Add support for showing a multi-dvm chain in the graph based visualizer
- Add a real-time mode where the pages will auto update (currently the user must refresh the page)
- ... Add support for user requested features!

## Acknowledgements
There are some fantastic people working in the DVM space right now. Thank you to [npub1drvpzev3syqt0…0eseet](https://njump.me/npub1drvpzev3syqt0kjrls50050uzf25gehpz9vgdw08hvex7e0vgfeq0eseet) for making python bindings for nostr_sdk and for the recent asyncio upgrades! Thank you to [npub1nxa4tywfz9nqp…uaa6q8](https://njump.me/npub1nxa4tywfz9nqp7z9zp7nr7d4nchhclsf58lcqt5y782rmf2hefjquaa6q8) for answering lots of questions about DVMs and for making the nostrdvm library. Thank you to [npub1l2vyh47mk2p0q…utajft](https://njump.me/npub1l2vyh47mk2p0qlsku7hg0vn29faehy9hy34ygaclpn66ukqp3afqutajft) for making the original DVM NIP and [vendata.io](https://vendata.io/) which I use all the time for testing!

P.S. I rushed to get this out in time for Nostriga 2024; code refactoring will be coming :)

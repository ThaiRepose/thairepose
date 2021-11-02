## TR-CACHING

This package is build for caching photo and data from google map api.
Because of the buget of our team that have a limit so I'm decide to create our own caching.
Why we not use external caching system? Because I have go thought a lot of caching system that let people use it for free
but I found a problem that caching system such as redis is a low-level caching so itn't build for caching image and in the well know caching system
[ NGINX cache ] We don't have hardware, tools, computer to test it make us decide to make our own caching system.

## What TR-CACHING can do.
- Save temporary data from everythin that you want to keep it.
- Data that we keep in cache can have an expire date or if you don't want it you can keep leave it alone.
- `tr-caching start` is a command to check cache file that have key word in filename is searchresult(json data) and download image form it(each place in search result should have photo reference but if place not have photo reference it would ignore it.).

## Installation

command run in thairepose directory
```
pip install src\caching\.
```
### command avaliable
`tr-caching start` start caching image system.

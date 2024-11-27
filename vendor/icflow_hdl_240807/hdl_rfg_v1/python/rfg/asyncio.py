import asyncio
import threading

## Low Level utils
##################
#rfgLock : asyncio.Lock | None = None 
rfgLock = asyncio.Lock()

def initIOLock():
    #rfgLock = asyncio.Lock()
    #print("Init Lock is: "+str(rfgLock))
    return getIOLock()

def getIOLock() -> asyncio.Lock:
    #print("Lock is: "+str(rfgLock))
    return rfgLock

loops = {}

def asyncWorker(name:str, loop : asyncio.AbstractEventLoop, startedBarrier: threading.Barrier, coro):
    #new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    #loops[name]['loop'] = new_loop
    #print("Worker got coroutine: "+str(asyncio.iscoroutine(coro)))
    #asyncio.run(coro)

    try:
        startedBarrier.wait()
        loop.run_until_complete(coro)
        
        #mainTask = loop.create_task(coro)
        #startedBarrier.wait()
        #loop.run_forever()
        #print("Stopped I/O Loop")
        loop.close()
        #new_loop.run_until_complete(coro)
    except e:
        print("Exception: "+str(e))
        pass
    #new_loop.run_forever()
    #print("Thread done")
    #return

def startNewEventLoop(name:str,coro ):
    """Start provided coroutine in a new Thread with a new event loop"""
    new_loop = asyncio.new_event_loop()
    startedBarrier = threading.Barrier(2, timeout=5)
    loops[name] = { 'loop': new_loop }
    th = threading.Thread(target=asyncWorker,args=[name,new_loop,startedBarrier,coro])
    loops[name]["thread"] = th
    th.start()
    startedBarrier.wait()
    #print("Finished Thread for "+name)


## I/O Event Loop
#####################
def startIOLoop(coro ):
    startNewEventLoop("io",coro)
    pass

def stopIOLoop():
    loops["io"]["loop"].stop()
    pass

def scheduleIOTask(coro ):
    loops["io"]["loop"].create_task(coro)

## UI Loop
###############
def startUILoop(coro):
    startNewEventLoop("ui",coro)
    pass

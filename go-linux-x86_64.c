// https://go.dev/src/runtime/runtime2.go
struct g {
    // Stack parameters
    void* stack;
    void* stackguard0;
    void* stackguard1;

    // Inner structures
    struct _panic* _panic;
    struct _defer* _defer;
    struct m* m;
    void* sched;
    void* syscallsp;
    void* syscallpc;
    void* syscallbp;
    void* stktopsp;

    // Generic parameter field
    void* param;
    void* atomicstatus;
    uint32_t stackLock;
    uint64_t goid;
    void* schedlink;
    int64_t waitsince;
    void* waitreason;

    // Preemption-related fields
    bool preempt;
    bool preemptStop;
    bool preemptShrink;

    bool asyncSafePoint;

    // Additional flags and states
    bool paniconfault;
    bool gcscandone;
    bool throwsplit;
    bool activeStackChans;
    void* parkingOnChan;
    bool inMarkAssist;
    bool coroexit;

    int8_t raceignore;
    bool nocgocallback;
    bool tracking;
    uint8_t trackingSeq;
    int64_t trackingStamp;
    int64_t runnableTime;
    void* lockedm;
    uint32_t sig;
    void* writebuf;
    void* sigcode0;
    void* sigcode1;
    void* sigpc;
    uint64_t parentGoid;
    void* gopc;
    void* ancestors;
    void* startpc;
    void* racectx;
    struct sudog* waiting;
    void* cgoCtxt;
    void* labels;
    struct timer* timer;
    int64_t sleepWhen;
    void* selectDone;

    void* goroutineProfiled;

    struct coro* coroarg;

    // Per-G tracer state
    void* trace;

    // Per-G GC state
    int64_t gcAssistBytes;
};

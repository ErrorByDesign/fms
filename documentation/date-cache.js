const DateCache = {
    PRECISION_SECONDS: {
        day: 86400,
        hour: 3600,
        minute: 60,
        second: 1
    },
    RANGE_MULTIPLIER: {
        day: 1,
        week: 0.75,
        minimonth: 0.75,
        month: 0.5,
        year: 0.25
    },
    RANGE_SECONDS: {
        day: 86400,
        week: 86400 * 7,
        month: 86400 * 30,
        year: 86400 * 365
    },
    // EXTERNAL
    external: {
        // LOAD JSON (ASYNC)
        async loadJSON(path) {
            try {
                const response = await fetch(path);
                return await response.json();
            } catch (error) {
                Debug.open("« ERROR: json »");
                Debug.error("Unable to load from JSON");
                throw error;
            }
        },
        // LOAD TEXT (ASYNC)
        async loadText(path) {
            try {
                const response = await fetch(path);
                return await response.text();
            } catch (error) {
                Debug.open("« ERROR: text »");
                Debug.error("Unable to load from TEXT file");
                throw error;
            }
        }
    },
    // HOLIDAYS
    holidays: {
        PATH: {
            relative: "./data/holidays.json",
            android:
                "/storage/emulated/0/Files/Code/Code Editor/Mother/FMS/data/holidays.json",
            desktop:
                "C:\\Files\\Developer\\VSCode\\Mother\\Area51\\data\\holidays.json"
        },
        STORAGE_KEY: STORAGE_KEYS.MARKET_HOLIDAYS,
        DAY: 86400,
        HOUR: 3600,
        MARKET_OPEN_UTC: {
            h: 14,
            m: 30
        },
        MARKET_CLOSE_UTC: {
            h: 21,
            m: 30
        },
        HOLIDAY_ANCHOR_UTC: {
            h: 18,
            m: 30
        },
        HOLIDAY_CACHE: null,
        // UTC DAY
        utcDay(epoch) {
            return new Date(epoch * 1000).getUTCDay(); // 0–6
        },
        // BUILD HOLIDAY ANCHOR
        buildHolidayAnchor(epoch) {
            const d = new Date(epoch * 1000);
            const anchor = Math.floor(
                Date.UTC(
                    d.getUTCFullYear(),
                    d.getUTCMonth(),
                    d.getUTCDate(),
                    this.HOLIDAY_ANCHOR_UTC.h,
                    this.HOLIDAY_ANCHOR_UTC.m,
                    0
                ) / 1000
            );
            return anchor;
        },
        // COMPUTE HOLIDAY BOUNDS
        computeHolidayBounds(holidaysArray) {
            if (!Array.isArray(holidaysArray)) {
                Debug.open("« ERROR »");
                Debug.warn("Invalid input: not array.");
                return [];
            }
            const result = holidaysArray
                .map(h => {
                    const anchorEpoch = this.buildHolidayAnchor(h.epoch);
                    const day = this.utcDay(anchorEpoch);
                    const type = h.type === "half" ? "half" : "full";
                    let preClose;
                    let postOpen;
                    if (type === "half") {
                        preClose = anchorEpoch;
                        postOpen =
                            day === 5
                                ? anchorEpoch + (20 + 48) * this.HOUR
                                : anchorEpoch + 20 * this.HOUR;
                    } else {
                        if (day === 1) {
                            preClose = anchorEpoch - 69 * this.HOUR;
                            postOpen = anchorEpoch + 20 * this.HOUR;
                        } else if (day === 5) {
                            preClose = anchorEpoch - 21 * this.HOUR;
                            postOpen = anchorEpoch + 68 * this.HOUR;
                        } else {
                            preClose = anchorEpoch - 21 * this.HOUR;
                            postOpen = anchorEpoch + 20 * this.HOUR;
                        }
                    }
                    return {
                        name: h.name || "",
                        type,
                        anchorEpoch,
                        preClose,
                        postOpen
                    };
                })
                .sort((a, b) => a.anchorEpoch - b.anchorEpoch);
            Debug.log("Count (output):", result.length);
            return result;
        },
        // ASYNC: LOAD AND NORMALIZE HOLIDAYS
        async importAndNormalizeHolidays() {
            Debug.log(" \nChecking device and storage path...");
            const getHolidaysPath = () => {
                const isAndroid = /Android/i.test(navigator.userAgent);
                Debug.log("Device is Android:", isAndroid);
                Debug.log("...checked device and storage path.\n ");
                return isAndroid ? this.PATH.relative : this.PATH.desktop;
            };
            const raw = await DateCache.external.loadJSON(getHolidaysPath());
            const holidaysArray = Object.values(raw).flat();
            Debug.log(" \nComputing holiday bounds...");
            const computed = this.computeHolidayBounds(holidaysArray);
            Debug.log("...computed holiday bounds.\n ");
            const shaped = computed.map(h =>
                DateCache.structure.marketHoliday(h)
            );
            this.HOLIDAY_CACHE = shaped;
            DateCache.save(this.STORAGE_KEY, shaped, "static");
            Debug.log(" \nHolidays (raw):", holidaysArray.length);
            Debug.log("Holidays (cached):", shaped.length, "\n ");
            return shaped;
        },
        // ASYNC: GET HOLIDAY CALENDAR
        async getHolidayCalendar() {
            Debug.log(" \nGetting holiday calendar...");
            if (this.HOLIDAY_CACHE) {
                Debug.log("...got holiday calendar from cache.\n ");
                return this.HOLIDAY_CACHE;
            }
            const cached = DateCache.load(this.STORAGE_KEY);
            if (cached?.data && Array.isArray(cached?.data)) {
                this.HOLIDAY_CACHE = cached.data;
                Debug.log("...got holiday calendar from storage cache.\n ");
                return this.HOLIDAY_CACHE;
            }
            Debug.log("...no holiday calendar.");
            Debug.log(" \nImporting and normalizing holidays...");
            Debug.subgroup("{ Import and Normalize Holidays }");
            const result = await this.importAndNormalizeHolidays();
            Debug.end();
            Debug.log("...imported and normalized holidays.\n ");
            return result;
        },
        // FIND ACTIVE HOLIDAY
        findActiveHoliday(nowEpoch) {
            Debug.log(" \nFinding active holiday...");
            for (const h of this.HOLIDAY_CACHE) {
                if (nowEpoch >= h.preClose && nowEpoch < h.postOpen) {
                    Debug.log("...found active holiday.");
                    return h;
                }
                if (nowEpoch < h.preClose) break;
            }
            Debug.log("...not found active holiday.");
            return null;
        },
        // FIND NEXT HOLIDAY
        findNextHoliday(nowEpoch) {
            Debug.log("Finding next holiday...");
            const found = this.HOLIDAY_CACHE.find(h => h.preClose > nowEpoch);
            if (!found) {
                Debug.open("« WARNING »");
                Debug.warn("...next holiday not found.\n ");
                return null;
            } else {
                Debug.log("...found next holiday.\n ");
                return found;
            }
        },
        // GET HOLIDAY STATE
        getHolidayState(nowEpoch) {
            Debug.log(" \nGetting holiday state...");

            Debug.subgroup("{ Holiday State }");

            const active = this.findActiveHoliday(nowEpoch);
            const next = this.findNextHoliday(
                active ? active.postOpen : nowEpoch
            );

            Debug.subgroup("< Holiday Details >");
            Debug.log(" \nActive holiday:", active?.name || "none");
            Debug.log(`Next holiday: ${next.name || "none"}\n `);
            Debug.end();
            Debug.end();

            Debug.log("...got holiday state.\n ");

            return {
                active,
                next
            };
        }
    },
    // MARKET
    market: {
        OPEN_UTC: 14 * 3600 + 30 * 60,
        CLOSE_UTC: 21 * 3600 + 30 * 60,
        DAY: 86400,
        // IS WEEKEND
        isWeekend(epoch) {
            Debug.log(" \nChecking if today is a weekend...");
            const d = new Date(epoch * 1000).getUTCDay();
            Debug.log("...checked if today is a weekend.");
            return d === 0 || d === 6;
        },
        // GET TODAY OPEN CLOSE
        getTodayOpenClose(epoch) {
            Debug.log("Getting todays open and close...");

            const d = new Date(epoch * 1000);
            const y = d.getUTCFullYear();
            const m = d.getUTCMonth();
            const day = d.getUTCDate();
            const open = Math.floor(Date.UTC(y, m, day, 14, 30, 0) / 1000);
            const close = Math.floor(Date.UTC(y, m, day, 21, 30, 0) / 1000);

            Debug.log("...got todays open and close.\n ");
            return {
                open,
                close
            };
        },
        // GET STATE
        getState(nowEpoch) {
            Debug.group("[ GET STATE ]");

            // PHASE 1: holiday override
            const holidays = DateCache.holidays.getHolidayState(nowEpoch);
            const isHoliday = holidays.active !== null;
            if (holidays.active) {
                Debug.end();
                return {
                    isOpen: false,
                    nextEvent: {
                        type: "open",
                        epoch: holidays.active.postOpen
                    },
                    holidays
                };
            }

            Debug.log(" \nGetting market state...");
            Debug.subgroup("{ Market State }");

            // PHASE 2: weekend check
            const isWeekend = this.isWeekend(nowEpoch);
            if (isWeekend) {
                const { open } = this.getTodayOpenClose(nowEpoch);
                let nextOpen = open;
                while (this.isWeekend(nextOpen)) {
                    nextOpen += this.DAY;
                }
                Debug.log("Next open (epoch):", nextOpen);
                Debug.log("Next open (PH):", formatDateTime(nextOpen, "MNL"));
                Debug.end();
                Debug.end();
                return {
                    isOpen: false,
                    nextEvent: {
                        type: "open",
                        epoch: nextOpen
                    },
                    holidays
                };
            }

            // PHASE 3: Weekday trading hours
            const { open, close } = this.getTodayOpenClose(nowEpoch);

            Debug.subgroup("< Market Details >");

            let isOpen = false;
            let nextEvent = null;
            let nowLog = "";
            if (nowEpoch >= open && nowEpoch < close) {
                isOpen = true;
                nextEvent = {
                    type: "Market close",
                    epoch: close
                };
                nowLog = "Market open";
            } else if (nowEpoch < open) {
                nextEvent = {
                    type: "Market open",
                    epoch: open
                };
                nowLog = "Pre-market";
            } else {
                nextEvent = {
                    type: "Market open",
                    epoch: open + this.DAY
                };
                nowLog = "After-hours";
            }

            // PHASE 4: Upcoming holiday pre-close
            if (holidays.next && holidays.next.preClose < nextEvent.epoch) {
                Debug.log("Pre-close override:", holidays.next.name);
                nextEvent = {
                    type: "Market close",
                    epoch: holidays.next.preClose
                };
            }

            Debug.log(" \nMarket is open:", isOpen);
            Debug.log("Today is a holiday:", isHoliday);
            Debug.log("Today is a weekend:", isWeekend);
            Debug.log(`Current state: ${nowLog}\n `);

            Debug.subgroup("< Next Market Event Details >");
            Debug.log(" \nNext type:", nextEvent.type);
            Debug.log("Next date:", nextEvent.epoch);
            Debug.log(`${formatDateTime(nextEvent.epoch, "MNL")}\n `);
            Debug.end();

            Debug.subgroup("< Open and Close Times >");
            Debug.log(" \nOpen (epoch):", open);
            Debug.log(formatDateTime(open, "MNL"));
            Debug.log("Close (epoch):", close);
            Debug.log(`${formatDateTime(close, "MNL")}\n `);
            Debug.end();
            Debug.end();

            Debug.end();
            Debug.log("...got market state.\n ");

            Debug.end();
            return {
                isOpen,
                nextEvent,
                holidays
            };
        }
    },
    // COUNTDOWN
    countdown: {
        CountdownPrecision: {
            SECOND: {
                unit: "second",
                value: 1,
                label: "second"
            },
            MINUTE: {
                unit: "minute",
                value: 60,
                label: "minute"
            },
            HOUR: {
                unit: "hour",
                value: 3600,
                label: "hour"
            },
            DAY: {
                unit: "day",
                value: 86400,
                label: "day"
            }
        },
        CountdownThresholds: [
            {
                remaining: 2,
                precision: {
                    unit: "day",
                    value: 86400,
                    label: "day"
                },
                interval: 86400
            },
            {
                remaining: 2,
                precision: {
                    unit: "hour",
                    value: 3600,
                    label: "hour"
                },
                interval: 3600
            },
            {
                remaining: 2,
                precision: {
                    unit: "hour",
                    value: 3600,
                    label: "hour"
                },
                interval: 900
            },
            {
                remaining: 15,
                precision: {
                    unit: "minute",
                    value: 60,
                    label: "minute"
                },
                interval: 300
            },
            {
                remaining: 5,
                precision: {
                    unit: "minute",
                    value: 60,
                    label: "minute"
                },
                interval: 60
            },
            {
                remaining: 2,
                precision: {
                    unit: "minute",
                    value: 60,
                    label: "minute"
                },
                interval: 15
            },
            {
                remaining: 1,
                precision: {
                    unit: "minute",
                    value: 60,
                    label: "minute"
                },
                interval: 5
            },
            {
                remaining: 15,
                precision: {
                    unit: "second",
                    value: 1,
                    label: "second"
                },
                interval: 1
            }
        ],
        // GET COUNTDOWN INTERVAL
        getCountdownInterval(secondsRemaining) {
            for (const threshold of this.CountdownThresholds) {
                const thresholdSeconds =
                    threshold.remaining * threshold.precision.value;
                if (secondsRemaining >= thresholdSeconds) {
                    return threshold.interval;
                }
            }
            return 1;
        },
        // GET COUNTDOWN INTERVAL
        getCountdownLabel(secondsRemaining) {
            for (const threshold of this.CountdownThresholds) {
                const thresholdSeconds =
                    threshold.remaining * threshold.precision.value;
                if (secondsRemaining >= thresholdSeconds) {
                    return threshold.precision.label;
                }
            }
            return 1;
        },
        // FORMAT COUNTDOWN
        formatCountdown(secondsRemaining) {
            const days = Math.floor(secondsRemaining / 86400);
            const hours = Math.floor((secondsRemaining % 86400) / 3600);
            const minutes = Math.floor((secondsRemaining % 3600) / 60);
            const seconds = secondsRemaining % 60;
            // ≥ 2 days → days only
            if (days >= 2) {
                return `${days} days`;
            }
            // < 2 days but ≥ 24h → hours only
            if (days === 1) {
                return `${hours + 24} hours`;
            }
            // < 2 hours → hours + minutes
            if (hours >= 1) {
                return minutes > 0
                    ? `${hours} hour${hours !== 1 ? "s" : ""} ${minutes} minutes`
                    : `${hours} hour${hours !== 1 ? "s" : ""}`;
            }
            // < 1 hour → minutes
            if (minutes >= 1) {
                return `${minutes} minutes`;
            }
            // final seconds
            return `${seconds} seconds`;
        },
        // COUNTDOWN MANAGER CLASS
        CountdownManager: class {
            constructor(targetEpoch) {
                Debug.group("{ Countdown Manager: Constructor }");
                this.targetEpoch = targetEpoch;
                this.intervalId = null;
                this.callbacks = [];
                Debug.log(" \nTarget epoch:", targetEpoch);
                Debug.log(formatDateTime(targetEpoch, "MNL") + "\n ");
                Debug.end();
            }
            // START
            start() {
                Debug.subgroup("{ Start }");
                this.update();
                this.scheduleNext();
                Debug.end();
            }
            // UPDATE
            update() {
                Debug.log(" \nUpdating...");
                const now = Math.floor(Date.now() / 1000);
                Debug.subgroup("< Update Details >");
                Debug.log(" \nNow:", now);
                Debug.log(formatDateTime(now, "MNL") + "\n ");
                const remaining = this.targetEpoch - now;
                if (remaining <= 0) {
                    this.stop();
                    this.notify({
                        expired: true,
                        remaining: 0
                    });
                    Debug.log("Expired:", true);
                    Debug.end();
                    Debug.log("...updated.\n ");
                    return;
                }
                const formatted =
                    DateCache.countdown.formatCountdown(remaining);
                this.notify({
                    expired: false,
                    remaining,
                    formatted
                });
                Debug.end();
                Debug.log("...updated.\n ");
            }
            // SCHEDULE NEXT
            scheduleNext() {
                Debug.log(" \nScheduling next...");
                const now = Math.floor(Date.now() / 1000);
                const remaining = this.targetEpoch - now;
                const intervalSeconds =
                    DateCache.countdown.getCountdownInterval(remaining);
                const intervalMs = intervalSeconds * 1000;
                const intervalLabel =
                    DateCache.countdown.getCountdownLabel(remaining);
                Debug.subgroup("< Next Schedule Details >");
                Debug.log(" \nNow:", now);
                Debug.log("Remaining:", remaining);
                Debug.log(
                    `Next interval (s): ${intervalSeconds} (${intervalLabel})\n `
                );
                Debug.end();
                this.intervalId = setTimeout(() => {
                    this.update();
                    this.scheduleNext();
                }, intervalMs);
                Debug.log("...scheduled next.\n ");
            }
            // STOP
            stop() {
                Debug.log(" \nStopping...");
                if (this.intervalId) {
                    clearTimeout(this.intervalId);
                    this.intervalId = null;
                    Debug.log("Timer cleared.");
                } else {
                    Debug.log("No active timer.");
                }
                Debug.log("...stopped.\n ");
            }
            // ON UPDATE
            onUpdate(callback) {
                Debug.log(" \nOn Updating...");
                this.callbacks.push(callback);
                Debug.log("Callback count:", this.callbacks.length);
                Debug.log("...on updated.\n ");
            }
            // NOTIFY
            notify(data) {
                Debug.log("Notifying...");
                Debug.subgroup("< Notify Details >");
                Debug.log(" \nCallbacks:", this.callbacks.length);
                Debug.log("Expired:", data.expired);
                Debug.log("Remaining:", data.remaining);
                Debug.log("Formatted:", data.formatted + "\n ");
                Debug.end();
                this.callbacks.forEach(cb => cb(data));
                Debug.log("...notified.\n ");
            }
        },
        // COUNTDOWN MODULE
        countdown: {
            managers: new Map(),
            // START
            start(key, targetEpoch, callback) {
                Debug.group(`[ COUNTDOWN: Start ] → ${key}`);
                if (this.managers.has(key)) {
                    Debug.log(" \nExisting manager found → stopping.");
                    this.managers.get(key).stop();
                }
                const manager = new DateCache.countdown.CountdownManager(
                    targetEpoch
                );
                manager.onUpdate(callback);
                manager.start();
                this.managers.set(key, manager);
                Debug.log(" \nActive managers:", this.managers.size, "\n ");
                Debug.end();
            },
            // STOP
            stop(key) {
                Debug.subgroup(`{ STOP } → ${key}`);
                if (this.managers.has(key)) {
                    this.managers.get(key).stop();
                    Debug.log(" \nExisting manager stopped:", key);
                    this.managers.delete(key);
                    Debug.log("Key deleted.");
                } else {
                    Debug.open("‹ WARNING ›");
                    Debug.warn("No manager for key:", key);
                }
                Debug.log(" \nActive managers:", this.managers.size, "\n ");
                Debug.end();
            }
        }
    },
    // STRUCTURE
    structure: {
        // MARKET HOLIDAYS
        marketHoliday: function (h) {
            if (!h || typeof h !== "object") {
                Debug.open("« ERROR: market holidays structure »");
                Debug.error("Invalid input: holidays data required.");
                throw new Error("Invalid input: holidays data required.");
            }
            return {
                name: h.name || "",
                type: h.type === "half" ? "half" : "full",
                anchorEpoch: Number(h.anchorEpoch) || 0,
                preClose: Number(h.preClose) || 0,
                postOpen: Number(h.postOpen) || 0
            };
        },
        // METRICS
        metrics: function (metricsRaw, price, change) {
            if (!metricsRaw || typeof price !== "number") {
                Debug.open("« ERROR: metrics structure »");
                Debug.error("Invalid input: metrics data required.");
                throw new Error("Invalid input: metrics data required.");
            }
            return {
                // METRICS (NUMERIC, UNFORMATTED)
                priceBid: metricsRaw.priceBid,
                priceMinimum: metricsRaw.priceMinimum,
                priceMaximum: metricsRaw.priceMaximum,
                percentDiscount: metricsRaw.percentDiscount,
                percentMinimum: metricsRaw.percentMinimum,
                percentMaximum: metricsRaw.percentMaximum,
                // BLOCKS
                blockMin: metricsRaw.blockMin,
                blockMinDouble: metricsRaw.blockMinDouble,
                blockMaxHalf: metricsRaw.blockMaxHalf,
                blockMax: metricsRaw.blockMax,
                // COST
                costMin: metricsRaw.costMin,
                costMinDouble: metricsRaw.costMinDouble,
                costMaxHalf: metricsRaw.costMaxHalf,
                costMax: metricsRaw.costMax,
                // COMMISSIONS
                commsMin: metricsRaw.commsMin,
                commsMinDouble: metricsRaw.commsMinDouble,
                commsMaxHalf: metricsRaw.commsMaxHalf,
                commsMax: metricsRaw.commsMax,
                // TOTAL
                totalMin: metricsRaw.totalMin,
                totalMinDouble: metricsRaw.totalMinDouble,
                totalMaxHalf: metricsRaw.totalMaxHalf,
                totalMax: metricsRaw.totalMax,
                // SELL
                sellMin: metricsRaw.sellMin,
                sellMinDouble: metricsRaw.sellMinDouble,
                sellMaxHalf: metricsRaw.sellMaxHalf,
                sellMax: metricsRaw.sellMax,
                // PROFIT
                profitMin: metricsRaw.profitMin,
                profitMinDouble: metricsRaw.profitMinDouble,
                profitMaxHalf: metricsRaw.profitMaxHalf,
                profitMax: metricsRaw.profitMax,
                // QUOTE market (RAW)
                price: price,
                change: change,
                // SERIAL
                serial: metricsRaw.serial || ""
            };
        },
        // NEWS
        news: function (sortedFeed) {
            return {
                articles: sortedFeed.map(article => ({
                    title: article.title || "",
                    summary: article.summary || "",
                    source: article.source || "",
                    url: article.url || "",
                    image: article.banner_image || "",
                    label: article.overall_sentiment_label || "",
                    relevance: article.relevance_score || "0",
                    sentiment: article.overall_sentiment_score || "0",
                    published: article.time_published || ""
                }))
            };
        },
        // OVERVIEW
        overview: function (overviewRaw, ratingResult) {
            if (!overviewRaw) {
                Debug.open("« ERROR: overview structure »");
                Debug.error("Invalid input: overview data required.");
                throw new Error("Invalid input: overview data required");
            }
            const ratingScore = Number(ratingResult?.score) || 0;
            return {
                // ---- COMPANY INFO ----
                name: overviewRaw.name || "",
                exchange: overviewRaw.exchange || "",
                sector: overviewRaw.sector || "",
                industry: overviewRaw.industry || "",
                country: overviewRaw.country || "",
                website: overviewRaw.website || "",
                // ---- MARKET DATA ----
                marketCap: overviewRaw.marketCap || 0,
                weekHigh: overviewRaw.weekHigh || 0,
                weekLow: overviewRaw.weekLow || 0,
                target: overviewRaw.target || 0,
                // ---- ANALYST RATINGS (FLAT) ----
                ratingStrongBuy: overviewRaw.ratings?.strongBuy || 0,
                ratingBuy: overviewRaw.ratings?.buy || 0,
                ratingHold: overviewRaw.ratings?.hold || 0,
                ratingSell: overviewRaw.ratings?.sell || 0,
                ratingStrongSell: overviewRaw.ratings?.strongSell || 0,
                // ---- DERIVED ----
                ratingScore: ratingScore,
                // ---- DESCRIPTION ----
                description: overviewRaw.description || ""
            };
        }
    },
    // SAVE
    save(key, data, type) {
        Debug.subgroup(`{ Date Cache: Save } → ${key}`);
        if (!key || typeof key !== "string") {
            Debug.open("« ERROR: DateCache.save »");
            Debug.error("Invalid key:", key);
            Debug.end();
            throw new Error("Invalid key:", key);
        }
        var now = Math.floor(Date.now() / 1000);
        var cache = {
            data: data,
            timestamp: null,
            expiry: null,
            type: type
        };
        if (type === "static") {
            Debug.log(" \nType: static");
        } else if (type === "fixed") {
            if (!data || typeof data.epoch !== "number") {
                Debug.open("« ERROR: DateCache.save »");
                Debug.error("Fixed data type invalid or missing epoch date.");
                Debug.warn("No data saved.");
                Debug.end();
                throw new Error(
                    "Invalid data type or missing epoch date. \nFixed type requires epoch date. \nNo data saved."
                );
            }
            cache.timestamp = now;
            cache.expiry = data.epoch;
            Debug.log(" \nType: Fixed");
        } else if (type === "relative") {
            var range = DateCache.getRelativeRange(key, data);
            if (typeof range !== "number" || range <= 0) {
                Debug.open("« ERROR: DateCache.getRelativeRange »");
                Debug.error("Invalid or missing date-range:", range);
                Debug.warn("No data saved.");
                Debug.end();
                throw new Error(
                    "Invalid or missing date-range. \nNo data saved."
                );
            }
            cache.timestamp = now;
            cache.expiry = now + range;
            Debug.log(" \nType: Relative");
        } else {
            Debug.open("« ERROR: DateCache.save »");
            Debug.error(" \nUnknown error: no data saved.\n ");
            Debug.end();
            throw new Error(`Unknown error: no data saved.`);
        }
        Debug.log("Timestamp:", cache.timestamp);
        Debug.log("Expiry:", cache.expiry, "\n ");
        Debug.end();
        localStorage.setItem(key, JSON.stringify(cache));
    },
    // GET RELATIVE RANGE
    getRelativeRange(key, data) {
        Debug.log("Getting relative range...");
        let rel = 0;
        switch (key) {
            case "overview":
                rel = 86400 * 30;
                Debug.log("...got relative overview range:", rel);
                return rel;
            case "news":
                rel = Number(data.rangeSeconds) || 0;
                Debug.log("...got relative news range:", rel);
                return rel;
            default:
                Debug.log("...got relative range:", rel);
                return rel;
        }
    },
    // LOAD
    load(key) {
        Debug.subgroup(`{ Date Cache: Load } → ${key}`);
        if (!key || typeof key !== "string") {
            Debug.open("« ERROR: DateCache.load »");
            Debug.error("Invalid key:", key);
            Debug.end();
            throw new Error("Invalid key:", key);
        }
        const stored = localStorage.getItem(key);
        if (!stored) {
            Debug.log(" \nItem not stored: no data loaded.\n ");
            Debug.end();
            return null;
        }
        let cache;
        try {
            cache = JSON.parse(stored);
        } catch {
            localStorage.removeItem(key);
            Debug.open("‹ WARNING: DateCache.load ›");
            Debug.warn("Corrupt data:", key);
            Debug.end();
            return null;
        }
        const now = Math.floor(Date.now() / 1000);
        const expired = cache.expiry !== null && now >= cache.expiry;
        Debug.log("Data expired:", expired);
        Debug.end();
        return {
            data: cache.data,
            expired,
            timestamp: cache.timestamp || null,
            expiry: cache.expiry || null,
            type: cache.type
        };
    },
    // METRICS
    metrics: {
        // GENERATE SERIAL
        generateSerial(ticker, settings, nextEventEpoch) {
            console.log("Generating serial...");
            // Example: "AAPL_v5.1.4050.1712345600"
            const settingsKey = `${settings.activeDiscount}.${settings.activeFee}.${settings.activeMinimum}${settings.activeMaximum}`;
            const serial = `${ticker}_v${settingsKey}.${nextEventEpoch}`;
            Debug.log(`...generated serial: ${serial}`);
            return serial;
        },
        // SAVE METRICS
        saveMetrics(ticker, serial, metricsData) {
            Debug.log("Saving metrics...");
            if (!ticker || !serial || !metricsData) {
                Debug.open("« ERROR: DateCache.metrics.saveMetrics »");
                Debug.error("Invalid input.");
                Debug.warn("No data saved.");
                throw new Error("Invalid input \nNo data saved.");
            }
            const metricsKey = STORAGE_KEYS.METRICS(ticker);
            const indexKey = STORAGE_KEYS.INDEX_METRICS(ticker);
            const now = Math.floor(Date.now() / 1000);
            const cache = {
                serial,
                data: metricsData,
                timestamp: now
            };
            // Metrics validity is SERIAL-based, not time-based
            DateCache.save(cacheKey, cache, "fixed");
            Debug.log("Saved data: metrics");
            // Update metrics index
            let index = DateCache.load(indexKey);
            let serials = Array.isArray(index?.data) ? index.data : [];
            if (!serials.includes(serial)) {
                serials.push(serial);
                DateCache.save(indexKey, serials, "fixed");
                Debug.log("Saved data: serial");
            }
            Debug.log("...saved metrics.");
        },
        // FIND METRICS BY SERIAL
        findMetricsBySerial(ticker, targetSerial) {
            Debug.log("Finding metrics by serial...");
            const metricsKey = STORAGE_KEYS.METRICS(ticker);
            const cached = DateCache.load(metricsKey);
            if (
                cached &&
                cached.data &&
                cached.data.data &&
                cached.data.serial === targetSerial
            ) {
                Debug.log("...found metrics by serial.");
                return cached.data;
            }
            Debug.open("‹ WARNING: DateCache.metrics.findMetricsBySerial ›");
            Debug.warn("No metrics found.");
            return null;
        },
        // CLEAN UP INDEX - I N C O M P L E T E
        cleanupIndex(ticker) {
            Debug.log("Cleaning up index...");
            const indexKey = STORAGE_KEYS.INDEX_METRICS(ticker);
            const index = DateCache.load(indexKey);
            if (!index || !index.data) {
                Debug.open("‹ WARNING: DateCache.metrics.cleanupIndex ›");
                Debug.warn("...cleanup failed.");
                return null;
            } else {
                Debug.log("...cleaned up index.");
            }
            // Implementation would check each serial's validity
            // and remove stale entries. For Phase 1, this can be a placeholder.
        }
    }
};

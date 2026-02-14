(function() {
    // UTM Tracking
    document.querySelectorAll('a[data-telegram]').forEach(a => {
        try {
            const url = new URL(a.href);
            const params = new URLSearchParams(window.location.search);
            params.forEach((v, k) => url.searchParams.set(k, v));
            a.href = url.toString();
        } catch (e) { console.log("URL parsing error", e); }
    });
})();

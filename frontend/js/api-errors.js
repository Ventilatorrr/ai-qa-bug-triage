function formatApiError(detail, fallback = "Request failed. Please try again.") {
    if (typeof detail === "string" && detail.trim()) {
        return detail;
    }

    if (Array.isArray(detail)) {
        const messages = detail
            .filter(function (error) {
                return error && typeof error.msg === "string" && error.msg.trim();
            })
            .map(function (error) {
                // Pydantic prefixes custom validator messages; users only need the rule.
                return error.msg.replace(/^Value error, /, "");
            });

        if (messages.length > 0) {
            return messages.join(" ");
        }
    }

    return fallback;
}

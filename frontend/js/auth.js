// Shared authentication helpers for the authenticated page modules.
// The backend remains authoritative: these helpers only attach the stored
// token and return to login when it is missing or rejected.

export function redirectToLogin() {
    localStorage.removeItem("access_token");
    window.location.replace("/login.html");
}

function getCurrentAccessToken() {
    const token = localStorage.getItem("access_token");

    if (!token) {
        redirectToLogin();
        return null;
    }

    return token;
}

export async function authenticatedFetch(url, options = {}) {
    const token = getCurrentAccessToken();

    if (!token) {
        return null;
    }

    const response = await fetch(url, {
        ...options,
        headers: {
            ...options.headers,
            "Authorization": "Bearer " + token
        }
    });

    if (response.status === 401) {
        redirectToLogin();
        return null;
    }

    return response;
}

// Identifies the current user for display and preferences only. A malformed
// token yields null; the backend rejects it on the next authenticated request.
export function getCurrentUserId() {
    const token = getCurrentAccessToken();

    if (!token) {
        return null;
    }

    try {
        const payload = token.split(".")[1];
        return JSON.parse(atob(payload)).user_id;
    } catch (error) {
        return null;
    }
}

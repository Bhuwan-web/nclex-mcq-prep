// Store and retrieve user state (last start_from and page_size) in localStorage
function saveUserState(startFrom, pageSize) {
    localStorage.setItem('nclex_last_start_from', startFrom);
    localStorage.setItem('nclex_last_page_size', pageSize);
}

function getUserState() {
    return {
        startFrom: localStorage.getItem('nclex_last_start_from') || 0,
        pageSize: localStorage.getItem('nclex_last_page_size') || 10
    };
}

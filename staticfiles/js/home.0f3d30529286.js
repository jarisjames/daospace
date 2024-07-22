// Infinite scroll implementation adjusted to stop at the last page
let currentPage = 1;
let isLastPage = false; // Flag to indicate the last page

window.addEventListener('scroll', () => {
    // Only fetch more results if not at the last page and not currently loading
    if (!isLastPage && window.innerHeight + window.pageYOffset >= document.body.offsetHeight - 10 && !loadingIndicator.getAttribute('data-loading')) {
        fetchMoreResults();
    }
});

function fetchMoreResults() {
    if (loadingIndicator.getAttribute('data-loading')) {
        return; // Prevent multiple concurrent requests
    }

    loadingIndicator.setAttribute('data-loading', 'true');
    loadingIndicator.style.display = 'block';

    const query = new URLSearchParams(window.location.search).get('q') || '';
    const fetchURL = `/?q=${encodeURIComponent(query)}&page=${currentPage + 1}`;

    fetch(fetchURL)
        .then(response => response.text())
        .then(htmlContent => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(htmlContent, "text/html");
            const newContent = doc.querySelector(".main-content").innerHTML;

            if (newContent.trim() === "") {
                // No more content, mark as last page
                isLastPage = true;
                loadingIndicator.style.display = 'none';
                return;
            }

            contentEnd.insertAdjacentHTML('beforebegin', newContent);
            currentPage++;
            loadingIndicator.removeAttribute('data-loading');
            loadingIndicator.style.display = 'none';
        })
        .catch(error => {
            console.error('Error loading more results:', error);
            loadingIndicator.removeAttribute('data-loading');
        });
}


// Function to toggle likers visibility
function toggleLikers(id) {
    var likersDiv = document.getElementById(id);
    if (likersDiv.style.display === "none") {
        likersDiv.style.display = "block";
    } else {
        likersDiv.style.display = "none";
    }
}

function toggleReplies(id) {
    var repliesDiv = document.getElementById(id);
    if (repliesDiv.style.display === "none") {
        repliesDiv.style.display = "block";
    } else {
        repliesDiv.style.display = "none";
    }
}

function toggleEmojiReactions(id) {
    var emojiReactionsDiv = document.getElementById(id);
    if (emojiReactionsDiv.style.display === "none") {
        emojiReactionsDiv.style.display = "block";
    } else {
        emojiReactionsDiv.style.display = "none";
    }
}

function toggleEmojiUserList(id) {
    var div = document.getElementById(id);
    if (div.style.display === "none") {
        div.style.display = "block";
    } else {
        div.style.display = "none";
    }
}

function toggleAdvancedSearch() {
    const advancedSearch = document.getElementById('advancedSearch');
    if (advancedSearch.style.display === 'none' || advancedSearch.style.display === '') {
        advancedSearch.style.display = 'flex';
    } else {
        advancedSearch.style.display = 'none';
    }
}

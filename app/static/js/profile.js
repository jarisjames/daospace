document.addEventListener('DOMContentLoaded', function() {
    const generateCodeForm = document.getElementById('generateCodeForm');
    const uniqueCodeContainer = document.getElementById('uniqueCodeContainer');
    const uniqueCodeElement = document.getElementById('uniqueCode');
    const linkForumButton = document.getElementById('linkForumButton');

    generateCodeForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const formData = new FormData(generateCodeForm);
        const forumUsername = formData.get('forumUsername');
        const daoName = formData.get('daoName');

        // Send the form data to the server
        try {
            const response = await fetch(window.location.pathname, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });

            if (!response.ok) {
                throw new Error('Failed to generate unique code');
            }

            const data = await response.json();
            if (data.unique_code) {
                uniqueCodeElement.innerText = data.unique_code;
                uniqueCodeContainer.style.display = 'block';
                linkForumButton.style.display = 'block';
            } else {
                alert('Failed to generate unique code');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while generating the unique code');
        }
    });

    linkForumButton.addEventListener('click', async () => {
        const forumUsername = document.getElementById('forumUsername').value;
        const daoName = document.getElementById('daoName').value;
        const uniqueCode = uniqueCodeElement.innerText;
        const account = window.location.pathname.split('/')[1]; // Extract the account from the URL

        // Verify the forum data linking
        try {
            const response = await fetch(`/${account}/link_forum_data/`, {
                method: 'POST',
                body: JSON.stringify({
                    forumUsername: forumUsername,
                    daoName: daoName,
                    uniqueCode: uniqueCode
                }),
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });

            if (!response.ok) {
                throw new Error('Failed to link forum data');
            }

            const data = await response.json();
            if (data.success) {
                alert('Forum data linked successfully');
            } else {
                alert('Failed to link forum data: ' + data.message);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while linking the forum data');
        }
    });
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

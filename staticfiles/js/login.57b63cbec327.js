document.addEventListener('DOMContentLoaded', function() {
    const loginButton = document.getElementById('loginButton');
    const logoutButton = document.getElementById('logoutButton');

    // Check if MetaMask is installed
    if (typeof window.ethereum !== 'undefined') {
        console.log('MetaMask is installed!');
    } else {
        console.log('MetaMask is not installed!');
        alert('Please install MetaMask to use this feature.');
        return;
    }

    // Check if the user is already logged in
    const storedAccount = localStorage.getItem('ethAccount');
    if (storedAccount) {
        showProfileButton(storedAccount);
    }

    loginButton.addEventListener('click', async () => {
        try {
            // Request account access
            const accounts = await ethereum.request({ method: 'eth_requestAccounts' });
            const account = accounts[0];
            console.log('Connected account:', account);

            // Sign a message with the account
            const message = "Please sign this message to log in.";
            const signature = await ethereum.request({
                method: 'personal_sign',
                params: [message, account],
            });
            console.log('Signature:', signature);

            // Send the signature and the account to the backend for verification
            fetch('/verify_signature/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({
                    signature: signature,
                    account: account,
                    message: message,
                }),
            })
            .then(response => response.json())
            .then(data => {
                console.log('Server response:', data);
                if (data.success) {
                    // Save account in local storage
                    localStorage.setItem('ethAccount', account);
                    showProfileButton(account);
                } else {
                    alert('Failed to log in. Please try again.');
                }
            });
        } catch (error) {
            console.error('Error logging in:', error);
            alert('An error occurred during login. Please try again.');
        }
    });

    logoutButton.addEventListener('click', () => {
        localStorage.removeItem('ethAccount');
        hideProfileButton();
    });

    function showProfileButton(account) {
        // Update the UI to show the user is logged in
        document.getElementById('loginMessage').innerText = 'Logged in successfully';
        loginButton.style.display = 'none'; // Hide the login button
        // Show the profile button
        const profileButtonContainer = document.getElementById('profileButtonContainer');
        profileButtonContainer.style.display = 'block';
        const profileButton = document.getElementById('profileButton');
        profileButton.href = `/${account}`; // Set the profile URL without prefix
    }

    function hideProfileButton() {
        document.getElementById('loginMessage').innerText = '';
        loginButton.style.display = 'block'; // Show the login button
        const profileButtonContainer = document.getElementById('profileButtonContainer');
        profileButtonContainer.style.display = 'none'; // Hide the profile button
    }
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

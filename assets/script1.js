
    // Runs when the page loads to check if the field is pre-filled
    document.addEventListener('DOMContentLoaded', (event) => {
        toggleClearButton();
    });

    // Function to show/hide the button
    function toggleClearButton() {
        const input = document.getElementById('searchInput');
        const clearBtn = document.getElementById('searchClearBtn');
        
        if (input.value.length > 0) {
            // Show the button if there is text
            clearBtn.style.display = 'block';
        } else {
            // Hide the button if the input is empty
            clearBtn.style.display = 'none';
        }
    }

    // Function to clear the input and submit the form
    function clearSearchAndSubmit() {
        const searchInput = document.getElementById('searchInput');
        searchInput.value = '';
        
        // Hide the button immediately after clearing
        document.getElementById('searchClearBtn').style.display = 'none';
        
        // Submit the form to reload the page without the search query
        document.getElementById('searchForm').submit();
    }

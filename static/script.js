// Get the modal elements
const modal = document.getElementById('lightbox-modal');
const modalImg = document.getElementById('lightbox-image');
const closeBtn = document.querySelector('.lightbox-close');

// Get all image containers that should trigger the lightbox
const imageContainers = document.querySelectorAll('.image-container');

// Check if modal elements exist before adding listeners
if (modal && modalImg && closeBtn && imageContainers.length > 0) {
    // Add click listener to each image container
    imageContainers.forEach(container => {
        container.addEventListener('click', function() {
            modal.style.display = "block";
            modalImg.src = this.dataset.src; // Use data-src for full image
        });
    });

    // Add click listener to the close button
    closeBtn.addEventListener('click', function() {
        modal.style.display = "none";
    });

    // Add click listener to the modal background (to close if clicking outside image)
    modal.addEventListener('click', function(event) {
        // Close if the click is on the modal background itself, not the image
        if (event.target === modal) {
            modal.style.display = "none";
        }
    });
}

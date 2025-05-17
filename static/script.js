document.addEventListener('DOMContentLoaded', (event) => {
    // Lightbox functionality
    const modal = document.getElementById("lightbox-modal");
    const modalImg = document.getElementById("lightbox-img");
    const imageContainers = document.querySelectorAll('.chat-image');
    const closeBtn = document.querySelector(".lightbox-close");

    imageContainers.forEach(container => {
        container.addEventListener('click', function() {
            modal.style.display = "block";
            const src = this.dataset.originalSrc || this.src;
            modalImg.src = src;
        });
    });

    if (closeBtn) {
        closeBtn.addEventListener('click', function() {
            modal.style.display = "none";
        })
    }

    // Close lightbox if clicked outside the image
    modal.addEventListener('click', function(event) {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    })

    // Media Gallery Functionality
    const galleryButton = document.getElementById('gallery-button');
    const galleryModal = document.getElementById('media-gallery-modal');
    const galleryCloseBtn = document.querySelector('.gallery-close');
    const galleryGrid = document.getElementById('media-gallery-grid'); // Get grid for potential future interactions

    if (galleryButton && galleryModal) {
        galleryButton.addEventListener('click', function() {
            galleryModal.style.display = "block";
        })
    }

    if (galleryCloseBtn) {
        galleryCloseBtn.addEventListener('click', function() {
            galleryModal.style.display = "none";
        })
    }

    window.addEventListener('click', function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
        // Also handle closing the gallery modal if clicked outside its content area
        if (event.target == galleryModal) {
            galleryModal.style.display = "none";
        }
    })
});

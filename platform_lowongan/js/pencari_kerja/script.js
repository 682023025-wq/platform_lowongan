// Pencari Kerja Dashboard JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Sidebar toggle for mobile
    const sidebar = document.querySelector('.sidebar');
    
    // Confirm actions
    const confirmButtons = document.querySelectorAll('.btn-danger.delete-confirm');
    confirmButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm') || 'Apakah Anda yakin?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.style.borderColor = '#e74c3c';
                } else {
                    field.style.borderColor = '#ddd';
                }
            });

            if (!isValid) {
                e.preventDefault();
                alert('Mohon lengkapi semua field yang wajib diisi.');
            }
        });
    });

    // Auto-hide flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            message.style.transition = 'opacity 0.5s ease';
            setTimeout(() => message.remove(), 500);
        }, 5000);
    });

    // Active menu highlight
    const currentPath = window.location.pathname;
    const menuLinks = document.querySelectorAll('.sidebar-menu a');
    menuLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // Job search filter
    const searchInput = document.getElementById('job-search');
    const jobCards = document.querySelectorAll('.job-card');
    
    if (searchInput) {
        searchInput.addEventListener('keyup', function() {
            const searchTerm = this.value.toLowerCase();
            
            jobCards.forEach(card => {
                const title = card.querySelector('h3')?.textContent.toLowerCase() || '';
                const company = card.querySelector('.company')?.textContent.toLowerCase() || '';
                const location = card.querySelector('.location')?.textContent.toLowerCase() || '';
                
                if (title.includes(searchTerm) || company.includes(searchTerm) || location.includes(searchTerm)) {
                    card.style.display = '';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }

    // File upload preview
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const fileName = this.files[0]?.name;
            const fileNameDisplay = this.parentNode.querySelector('.file-name');
            if (fileNameDisplay && fileName) {
                fileNameDisplay.textContent = fileName;
            }
        });
    });
});

// Save job to favorites
async function saveJob(jobId) {
    try {
        const response = await fetch(`/pencari_kerja/save_job/${jobId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        const data = await response.json();
        if (data.success) {
            alert('Lowongan berhasil disimpan!');
        } else {
            alert(data.message || 'Gagal menyimpan lowongan');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Terjadi kesalahan, silakan coba lagi');
    }
}

// Apply to job
async function applyJob(jobId) {
    if (confirm('Apakah Anda yakin ingin melamar pekerjaan ini?')) {
        window.location.href = `/pencari_kerja/apply/${jobId}`;
    }
}

// AJAX utility function
async function fetchData(url, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        }
    };

    if (data) {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(url, options);
        return await response.json();
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}

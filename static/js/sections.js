document.addEventListener('DOMContentLoaded', function() {
    // Initialize all sections as collapsed except the first one
    const sections = document.querySelectorAll('.dashboard-section');
    sections.forEach((section, index) => {
        const header = section.querySelector('.section-header');
        const content = section.querySelector('.section-content');
        const toggleBtn = section.querySelector('.toggle-btn');
        
        // Expand first section by default
        if (index === 0) {
            content.classList.add('expanded');
        } else {
            toggleBtn.classList.add('collapsed');
        }

        header.addEventListener('click', () => {
            // Toggle current section
            content.classList.toggle('expanded');
            toggleBtn.classList.toggle('collapsed');
            
            // Save state to localStorage
            localStorage.setItem(`section-${section.id}`, content.classList.contains('expanded'));
        });

        // Restore state from localStorage
        const isExpanded = localStorage.getItem(`section-${section.id}`);
        if (isExpanded !== null) {
            if (isExpanded === 'true') {
                content.classList.add('expanded');
                toggleBtn.classList.remove('collapsed');
            } else {
                content.classList.remove('expanded');
                toggleBtn.classList.add('collapsed');
            }
        }
    });
});

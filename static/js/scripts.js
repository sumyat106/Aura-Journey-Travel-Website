document.addEventListener("DOMContentLoaded", function() {
    
    // 1. Mobile Menu Toggle
    const menuToggle = document.getElementById('mobile-menu-btn');
    const navContent = document.getElementById('nav-content');


    if (menuToggle && navContent) {
        menuToggle.addEventListener('click', function() {
            navContent.classList.toggle('show');
            // Change icon from bars to X
            const icon = menuToggle.querySelector('i');
            if (icon.classList.contains('fa-bars')) {
                icon.classList.replace('fa-bars', 'fa-xmark');
            } else {
                icon.classList.replace('fa-xmark', 'fa-bars');
            }
        });
        
    }

    // 2. Tab Table Auto-Scroll Indicator
    // (Helpful for users to know they can swipe the table)
    const tableContainers = document.querySelectorAll('.table-responsive');
    tableContainers.forEach(container => {
        container.addEventListener('scroll', function() {
            // Logic to hide a "scroll hint" if you add one
        });
    });

    // 3. Admin Actions (Demo Logic)
    document.querySelectorAll('.btn-approve').forEach(function(btn) {
        btn.onclick = function(e) {
            e.preventDefault();
            if(confirm("Are you sure you want to approve this booking?")) {
                btn.innerHTML = '<i class="fa fa-check"></i> Approved';
                btn.style.background = "#37be82";
                btn.style.color = "#fff";
                btn.closest('tr').style.opacity = "0.7";
            }
        }
    });

    document.querySelectorAll('.btn-reject').forEach(function(btn) {
        btn.onclick = function(e) {
            e.preventDefault();
            if(confirm("Reject this booking?")) {
                btn.innerHTML = '<i class="fa fa-times"></i> Rejected';
                btn.style.background = "#c02c1a";
                btn.style.color = "#fff";
            }
        }
    });

    // 4. Save Button Logic
    document.querySelectorAll('.save-btn').forEach(function(btn) {
        btn.onclick = function(e) {
            e.preventDefault();
            btn.classList.toggle('saved');
            if (btn.classList.contains('saved')) {
                btn.innerHTML = '<i class="fa fa-heart"></i> Saved';
                btn.style.background = "#37be82";
            } else {
                btn.innerHTML = '<i class="fa-regular fa-heart"></i> Save Trip';
                btn.style.background = "#222d35";
            }
        }

        
    });

});


document.addEventListener('DOMContentLoaded', () => {
  // Elements
  const studentsTableBody = document.getElementById('students-table-body');
  const recordsCounter = document.getElementById('records-counter');
  const filterStatusTag = document.getElementById('filter-status-tag');
  const filterSearch = document.getElementById('filter-search');
  const btnClearSearch = document.getElementById('btn-clear-search');
  const filterCourse = document.getElementById('filter-course');
  const filterBornAfter = document.getElementById('filter-born-after');
  const btnResetFilters = document.getElementById('btn-reset-filters');
  const btnRefresh = document.getElementById('btn-refresh');

  // Stats elements
  const statTotal = document.getElementById('stat-total-students');
  const statCourses = document.getElementById('stat-total-courses');
  const statEmail = document.getElementById('stat-with-email');
  const statPhone = document.getElementById('stat-with-phone');

  // Theme Elements
  const btnThemeToggle = document.getElementById('btn-theme-toggle');
  const themeIconSun = document.getElementById('theme-icon-sun');
  const themeIconMoon = document.getElementById('theme-icon-moon');

  // Export Elements
  const btnExportDropdown = document.getElementById('btn-export-dropdown');
  const exportMenu = document.getElementById('export-menu');
  const btnExportCsv = document.getElementById('btn-export-csv');
  const btnExportJson = document.getElementById('btn-export-json');

  // Analytics & Pills Containers
  const courseBarsContainer = document.getElementById('course-bars-container');
  const coursePillsContainer = document.getElementById('course-pills');

  // Modals
  const studentModal = document.getElementById('student-modal');
  const modalTitle = document.getElementById('modal-title');
  const studentForm = document.getElementById('student-form');
  const modalError = document.getElementById('modal-error');
  const btnAddStudent = document.getElementById('btn-add-student');
  const btnCloseModal = document.getElementById('btn-close-modal');
  const btnCancelModal = document.getElementById('btn-cancel-modal');
  const btnSaveText = document.getElementById('btn-save-text');

  // Form Inputs
  const inpStudentId = document.getElementById('inp-student-id');
  const inpName = document.getElementById('inp-name');
  const inpDob = document.getElementById('inp-dob');
  const inpCourse = document.getElementById('inp-course');
  const inpEmail = document.getElementById('inp-email');
  const inpPhone = document.getElementById('inp-phone');
  const inpEnrollment = document.getElementById('inp-enrollment');
  const inpAddress = document.getElementById('inp-address');

  // Profile View Modal
  const viewModal = document.getElementById('view-modal');
  const btnCloseView = document.getElementById('btn-close-view');
  const profileDetailBody = document.getElementById('profile-detail-body');
  const profileFooterActions = document.getElementById('profile-footer-actions');

  // Delete Confirmation Modal
  const deleteModal = document.getElementById('delete-modal');
  const deleteModalTitle = document.getElementById('delete-modal-title');
  const deleteModalDesc = document.getElementById('delete-modal-desc');
  const btnCancelDelete = document.getElementById('btn-cancel-delete');
  const btnConfirmDelete = document.getElementById('btn-confirm-delete');

  // AI Modal
  const aiModal = document.getElementById('ai-modal');
  const btnOpenAi = document.getElementById('btn-open-ai');
  const btnCloseAi = document.getElementById('btn-close-ai');
  const ollamaStatusBadge = document.getElementById('ollama-status-badge');
  const aiQueryInput = document.getElementById('ai-query-input');
  const btnSubmitAi = document.getElementById('btn-submit-ai');
  const aiLoader = document.getElementById('ai-loader');
  const aiResultPanel = document.getElementById('ai-result-panel');
  const aiSourceTag = document.getElementById('ai-source-tag');
  const aiRecordsTag = document.getElementById('ai-records-tag');
  const aiAnswerText = document.getElementById('ai-answer-text');
  const btnCopyAiAnswer = document.getElementById('btn-copy-ai-answer');

  // State
  let studentsData = [];
  let totalDatabaseCount = 0;
  let editingStudentId = null;
  let pendingDeleteId = null;
  let debounceTimeout = null;
  let sortKey = null;
  let sortOrder = null; // 'asc' or 'desc'
  let cachedDistribution = {};

  // Avatar Gradients Palette
  const AVATAR_GRADIENTS = [
    'linear-gradient(135deg, #6366f1, #8b5cf6)',
    'linear-gradient(135deg, #3b82f6, #06b6d4)',
    'linear-gradient(135deg, #10b981, #059669)',
    'linear-gradient(135deg, #f59e0b, #d97706)',
    'linear-gradient(135deg, #ec4899, #f43f5e)',
    'linear-gradient(135deg, #8b5cf6, #d946ef)',
    'linear-gradient(135deg, #0ea5e9, #38bdf8)'
  ];

  // ----------------------------------------------------
  // Initial Theme Setup
  // ----------------------------------------------------
  initTheme();

  function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    applyTheme(savedTheme);
  }

  function applyTheme(theme) {
    if (theme === 'light') {
      document.documentElement.setAttribute('data-theme', 'light');
      themeIconSun.classList.add('hidden');
      themeIconMoon.classList.remove('hidden');
    } else {
      document.documentElement.removeAttribute('data-theme');
      themeIconSun.classList.remove('hidden');
      themeIconMoon.classList.add('hidden');
    }
    localStorage.setItem('theme', theme);
  }

  btnThemeToggle.addEventListener('click', () => {
    const currentTheme = document.documentElement.getAttribute('data-theme') === 'light' ? 'light' : 'dark';
    const nextTheme = currentTheme === 'light' ? 'dark' : 'light';
    applyTheme(nextTheme);
  });

  // ----------------------------------------------------
  // Export Dropdown
  // ----------------------------------------------------
  btnExportDropdown.addEventListener('click', (e) => {
    e.stopPropagation();
    exportMenu.classList.toggle('hidden');
  });

  document.addEventListener('click', () => {
    if (!exportMenu.classList.contains('hidden')) {
      exportMenu.classList.add('hidden');
    }
  });

  btnExportCsv.addEventListener('click', exportToCsv);
  btnExportJson.addEventListener('click', exportToJson);

  function exportToCsv() {
    if (!studentsData || studentsData.length === 0) {
      showToast('No student records to export', 'error');
      return;
    }
    const headers = ['student_id', 'name', 'date_of_birth', 'course', 'email', 'phone', 'enrollment_date', 'address'];
    const csvRows = [headers.join(',')];

    studentsData.forEach(s => {
      const row = headers.map(h => {
        const val = s[h] ? String(s[h]).replace(/"/g, '""') : '';
        return `"${val}"`;
      });
      csvRows.push(row.join(','));
    });

    const csvContent = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csvRows.join('\n'));
    const link = document.createElement('a');
    link.setAttribute('href', csvContent);
    link.setAttribute('download', `academix_students_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    showToast(`Exported ${studentsData.length} records to CSV`, 'success');
  }

  function exportToJson() {
    if (!studentsData || studentsData.length === 0) {
      showToast('No student records to export', 'error');
      return;
    }
    const jsonStr = JSON.stringify(studentsData, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(jsonStr);
    const link = document.createElement('a');
    link.setAttribute('href', dataUri);
    link.setAttribute('download', `academix_students_${new Date().toISOString().slice(0, 10)}.json`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    showToast(`Exported ${studentsData.length} records to JSON`, 'success');
  }

  // ----------------------------------------------------
  // Initial Data Load
  // ----------------------------------------------------
  loadStudents();
  loadStats();
  checkOllamaStatus();

  // ----------------------------------------------------
  // Event Listeners
  // ----------------------------------------------------
  btnAddStudent.addEventListener('click', () => openModalForCreate());
  btnCloseModal.addEventListener('click', closeModal);
  btnCancelModal.addEventListener('click', closeModal);
  studentForm.addEventListener('submit', handleFormSubmit);

  btnCloseView.addEventListener('click', () => viewModal.classList.add('hidden'));

  btnCancelDelete.addEventListener('click', () => {
    deleteModal.classList.add('hidden');
    pendingDeleteId = null;
  });

  btnConfirmDelete.addEventListener('click', executeConfirmedDelete);

  btnOpenAi.addEventListener('click', () => {
    aiModal.classList.remove('hidden');
    checkOllamaStatus();
  });
  btnCloseAi.addEventListener('click', () => aiModal.classList.add('hidden'));
  btnSubmitAi.addEventListener('click', handleAiQuery);
  aiQueryInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleAiQuery();
  });

  btnCopyAiAnswer.addEventListener('click', () => {
    const text = aiAnswerText.textContent;
    if (text) {
      navigator.clipboard.writeText(text);
      btnCopyAiAnswer.querySelector('span').textContent = 'Copied!';
      setTimeout(() => {
        btnCopyAiAnswer.querySelector('span').textContent = 'Copy';
      }, 2000);
    }
  });

  // Suggestion chips
  document.querySelectorAll('.chip-query').forEach(chip => {
    chip.addEventListener('click', () => {
      aiQueryInput.value = chip.getAttribute('data-q');
      handleAiQuery();
    });
  });

  // Search & Filter Listeners
  filterSearch.addEventListener('input', () => {
    btnClearSearch.classList.toggle('hidden', !filterSearch.value.trim());
    clearTimeout(debounceTimeout);
    debounceTimeout = setTimeout(() => loadStudents(), 250);
  });

  btnClearSearch.addEventListener('click', () => {
    filterSearch.value = '';
    btnClearSearch.classList.add('hidden');
    loadStudents();
  });

  filterCourse.addEventListener('change', () => {
    updateActivePill(filterCourse.value);
    loadStudents();
  });

  filterBornAfter.addEventListener('change', () => loadStudents());

  btnResetFilters.addEventListener('click', () => {
    filterSearch.value = '';
    btnClearSearch.classList.add('hidden');
    filterCourse.value = '';
    filterBornAfter.value = '';
    sortKey = null;
    sortOrder = null;
    updateSortIcons();
    updateActivePill('');
    loadStudents();
    showToast('Filters reset', 'info');
  });

  btnRefresh.addEventListener('click', () => {
    loadStudents();
    loadStats();
    showToast('Records refreshed from SQLite', 'info');
  });

  // Sortable Headers
  document.querySelectorAll('.sortable-col').forEach(th => {
    th.addEventListener('click', () => {
      const key = th.getAttribute('data-sort');
      if (sortKey === key) {
        sortOrder = sortOrder === 'asc' ? 'desc' : (sortOrder === 'desc' ? null : 'asc');
        if (!sortOrder) sortKey = null;
      } else {
        sortKey = key;
        sortOrder = 'asc';
      }
      updateSortIcons();
      applySortingAndRender();
    });
  });

  function updateSortIcons() {
    document.querySelectorAll('.sortable-col').forEach(th => {
      const key = th.getAttribute('data-sort');
      const icon = th.querySelector('.sort-icon');
      th.classList.remove('sort-asc', 'sort-desc');

      if (sortKey === key) {
        if (sortOrder === 'asc') {
          icon.textContent = '▲';
          th.classList.add('sort-asc');
        } else if (sortOrder === 'desc') {
          icon.textContent = '▼';
          th.classList.add('sort-desc');
        }
      } else {
        icon.textContent = '↕';
      }
    });
  }

  // ----------------------------------------------------
  // Load Students API
  // ----------------------------------------------------
  async function loadStudents() {
    try {
      const search = filterSearch.value.trim();
      const course = filterCourse.value;
      const bornAfter = filterBornAfter.value;

      const params = new URLSearchParams();
      if (search) params.append('search', search);
      if (course) params.append('course', course);
      if (bornAfter) params.append('born_after', bornAfter);

      const url = `/students?${params.toString()}`;
      const res = await fetch(url);
      if (!res.ok) throw new Error('Failed to fetch students');

      const data = await res.json();
      studentsData = data.students;

      const isFiltered = search || course || bornAfter;
      filterStatusTag.classList.toggle('hidden', !isFiltered);
      if (isFiltered) {
        filterStatusTag.textContent = `Filtered (${data.total} found)`;
      }

      recordsCounter.textContent = data.total;
      applySortingAndRender();

      // Update courses in dropdown & pills
      updateCourseDropdown(data.students);
    } catch (err) {
      console.error(err);
      studentsTableBody.innerHTML = `
        <tr>
          <td colspan="8" class="empty-state">
            <p style="color: var(--color-rose);">Error connecting to backend server. Please verify FastAPI is running.</p>
          </td>
        </tr>
      `;
    }
  }

  // Apply sorting client-side
  function applySortingAndRender() {
    let list = [...studentsData];

    if (sortKey && sortOrder) {
      list.sort((a, b) => {
        let valA = a[sortKey] || '';
        let valB = b[sortKey] || '';
        if (typeof valA === 'string') valA = valA.toLowerCase();
        if (typeof valB === 'string') valB = valB.toLowerCase();

        if (valA < valB) return sortOrder === 'asc' ? -1 : 1;
        if (valA > valB) return sortOrder === 'asc' ? 1 : -1;
        return 0;
      });
    }

    renderStudentsTable(list);
  }

  // ----------------------------------------------------
  // Render Students Table
  // ----------------------------------------------------
  function renderStudentsTable(students) {
    if (!students || students.length === 0) {
      studentsTableBody.innerHTML = `
        <tr>
          <td colspan="8" class="empty-state">
            <p>No student records found matching the current search / filter.</p>
          </td>
        </tr>
      `;
      return;
    }

    studentsTableBody.innerHTML = students.map((s, index) => {
      const initials = getInitials(s.name);
      const gradient = getAvatarGradient(s.name);

      return `
        <tr class="student-row">
          <td class="student-id-cell">
            <span style="cursor: pointer;" title="Click to copy ID" onclick="window.copyToClipboard('${escapeHtml(s.student_id)}')">
              ${escapeHtml(s.student_id)}
            </span>
          </td>
          <td class="student-name-cell">
            <div class="name-with-avatar">
              <div class="student-avatar" style="background: ${gradient};">
                ${initials}
              </div>
              <span>${escapeHtml(s.name)}</span>
            </div>
          </td>
          <td>${escapeHtml(s.date_of_birth)}</td>
          <td>
            ${s.course ? `<span class="course-badge">${escapeHtml(s.course)}</span>` : '<span style="color:var(--text-muted);">-</span>'}
          </td>
          <td>
            ${s.email ? `<span style="cursor:pointer;" title="Click to copy email" onclick="window.copyToClipboard('${escapeHtml(s.email)}')">${escapeHtml(s.email)}</span>` : '<span style="color:var(--text-muted);">-</span>'}
          </td>
          <td>${s.phone ? escapeHtml(s.phone) : '<span style="color:var(--text-muted);">-</span>'}</td>
          <td>${s.enrollment_date ? escapeHtml(s.enrollment_date) : '<span style="color:var(--text-muted);">-</span>'}</td>
          <td class="actions-col">
            <div class="row-actions">
              <button class="action-btn" title="View Profile" onclick="window.viewStudent('${escapeHtml(s.student_id)}')">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"></path>
                  <circle cx="12" cy="12" r="3"></circle>
                </svg>
              </button>
              <button class="action-btn btn-edit" title="Edit Student" onclick="window.editStudent('${escapeHtml(s.student_id)}')">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                </svg>
              </button>
              <button class="action-btn btn-delete" title="Delete Student" onclick="window.promptDeleteStudent('${escapeHtml(s.student_id)}', '${escapeHtml(s.name)}')">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="3 6 5 6 21 6"></polyline>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                </svg>
              </button>
            </div>
          </td>
        </tr>
      `;
    }).join('');
  }

  // ----------------------------------------------------
  // Helpers: Avatars & Initials
  // ----------------------------------------------------
  function getInitials(name) {
    if (!name) return 'ST';
    const parts = name.trim().split(/\s+/);
    if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
  }

  function getAvatarGradient(name) {
    let hash = 0;
    for (let i = 0; i < (name || '').length; i++) {
      hash = name.charCodeAt(i) + ((hash << 5) - hash);
    }
    const index = Math.abs(hash) % AVATAR_GRADIENTS.length;
    return AVATAR_GRADIENTS[index];
  }

  window.copyToClipboard = function(text) {
    if (!text) return;
    navigator.clipboard.writeText(text);
    showToast(`Copied "${text}" to clipboard!`, 'info');
  };

  // ----------------------------------------------------
  // Dashboard Stats & Analytics
  // ----------------------------------------------------
  async function loadStats() {
    try {
      const res = await fetch('/students/stats/summary');
      if (res.ok) {
        const stats = await res.json();
        totalDatabaseCount = stats.total_students;
        animateCounter(statTotal, stats.total_students);
        animateCounter(statCourses, stats.courses_count);
        cachedDistribution = stats.course_distribution || {};

        renderAnalyticsBars(stats.course_distribution, stats.total_students);
        renderCoursePills(stats.course_distribution, stats.total_students);
      }

      const listRes = await fetch('/students?limit=100');
      if (listRes.ok) {
        const listData = await listRes.json();
        const emailCount = listData.students.filter(s => s.email).length;
        const phoneCount = listData.students.filter(s => s.phone).length;
        animateCounter(statEmail, emailCount);
        animateCounter(statPhone, phoneCount);
      }
    } catch (e) {
      console.warn("Could not load stats", e);
    }
  }

  // Smooth Number Counter Animation
  function animateCounter(element, target) {
    const current = parseInt(element.textContent, 10) || 0;
    if (current === target) return;
    const duration = 600;
    const start = performance.now();

    function step(timestamp) {
      const progress = Math.min((timestamp - start) / duration, 1);
      const val = Math.floor(progress * (target - current) + current);
      element.textContent = val;
      if (progress < 1) {
        requestAnimationFrame(step);
      } else {
        element.textContent = target;
      }
    }
    requestAnimationFrame(step);
  }

  // Render Analytics Progress Bars
  function renderAnalyticsBars(distribution, total) {
    if (!distribution || Object.keys(distribution).length === 0) {
      courseBarsContainer.innerHTML = '<p class="hint-text">No courses recorded yet.</p>';
      return;
    }

    const currentCourse = filterCourse.value;

    courseBarsContainer.innerHTML = Object.entries(distribution).map(([cName, count]) => {
      const pct = total > 0 ? Math.round((count / total) * 100) : 0;
      const isActive = currentCourse === cName;

      return `
        <div class="course-bar-item ${isActive ? 'active' : ''}" onclick="window.selectCourseFilter('${escapeHtml(cName)}')">
          <div class="course-bar-info">
            <span class="course-bar-name" title="${escapeHtml(cName)}">${escapeHtml(cName)}</span>
            <span class="course-bar-count">${count} (${pct}%)</span>
          </div>
          <div class="bar-track">
            <div class="bar-fill" style="width: ${pct}%;"></div>
          </div>
        </div>
      `;
    }).join('');
  }

  // Render Interactive Course Pills
  function renderCoursePills(distribution, total) {
    const currentVal = filterCourse.value;
    let html = `
      <div class="course-pill ${!currentVal ? 'active' : ''}" onclick="window.selectCourseFilter('')">
        <span>All Courses</span>
        <span class="pill-count">${total}</span>
      </div>
    `;

    Object.entries(distribution).forEach(([cName, count]) => {
      const isActive = currentVal === cName;
      html += `
        <div class="course-pill ${isActive ? 'active' : ''}" onclick="window.selectCourseFilter('${escapeHtml(cName)}')">
          <span>${escapeHtml(cName)}</span>
          <span class="pill-count">${count}</span>
        </div>
      `;
    });

    coursePillsContainer.innerHTML = html;
  }

  window.selectCourseFilter = function(courseName) {
    filterCourse.value = courseName;
    updateActivePill(courseName);
    loadStudents();
    renderAnalyticsBars(cachedDistribution, totalDatabaseCount);
  };

  function updateActivePill(courseName) {
    document.querySelectorAll('.course-pill').forEach(pill => {
      const pillText = pill.querySelector('span').textContent;
      const isAll = pillText === 'All Courses' && !courseName;
      const isMatch = pillText === courseName;
      pill.classList.toggle('active', isAll || isMatch);
    });
  }

  function updateCourseDropdown(students) {
    const currentVal = filterCourse.value;
    const existingOptions = new Set(Array.from(filterCourse.options).map(o => o.value));

    students.forEach(s => {
      if (s.course && !existingOptions.has(s.course)) {
        const opt = document.createElement('option');
        opt.value = s.course;
        opt.textContent = s.course;
        filterCourse.appendChild(opt);
        existingOptions.add(s.course);
      }
    });
    filterCourse.value = currentVal;
  }

  // ----------------------------------------------------
  // Modals & Profile Viewer
  // ----------------------------------------------------
  function openModalForCreate() {
    editingStudentId = null;
    modalTitle.textContent = "Add New Student";
    btnSaveText.textContent = "Save Student";
    studentForm.reset();
    inpStudentId.disabled = false;
    modalError.classList.add('hidden');
    studentModal.classList.remove('hidden');
  }

  window.editStudent = async function(studentId) {
    try {
      const res = await fetch(`/students/${studentId}`);
      if (!res.ok) throw new Error("Could not find student");
      const student = await res.json();

      editingStudentId = student.student_id;
      modalTitle.textContent = `Edit Student: ${student.student_id}`;
      btnSaveText.textContent = "Update Student";

      inpStudentId.value = student.student_id;
      inpStudentId.disabled = true; // Primary ID cannot be modified
      inpName.value = student.name || '';
      inpDob.value = student.date_of_birth || '';
      inpCourse.value = student.course || '';
      inpEmail.value = student.email || '';
      inpPhone.value = student.phone || '';
      inpEnrollment.value = student.enrollment_date || '';
      inpAddress.value = student.address || '';

      modalError.classList.add('hidden');
      viewModal.classList.add('hidden'); // Close view modal if open
      studentModal.classList.remove('hidden');
    } catch (err) {
      showToast(err.message, 'error');
    }
  };

  window.viewStudent = async function(studentId) {
    try {
      const res = await fetch(`/students/${studentId}`);
      if (!res.ok) throw new Error("Could not find student profile");
      const s = await res.json();

      const initials = getInitials(s.name);
      const gradient = getAvatarGradient(s.name);

      profileDetailBody.innerHTML = `
        <div class="profile-banner full" style="grid-column: span 2; margin: -20px -24px 16px;">
          <div class="profile-avatar-large" style="background: ${gradient};">
            ${initials}
          </div>
          <div class="profile-banner-info">
            <h3>${escapeHtml(s.name)}</h3>
            <span class="profile-banner-id">${escapeHtml(s.student_id)}</span>
          </div>
        </div>

        <div class="profile-field">
          <span class="profile-field-label">Student ID</span>
          <span class="profile-field-value" style="font-family: var(--font-mono); color: var(--accent-primary);">${escapeHtml(s.student_id)}</span>
        </div>

        <div class="profile-field">
          <span class="profile-field-label">Date of Birth</span>
          <span class="profile-field-value">${escapeHtml(s.date_of_birth)}</span>
        </div>

        <div class="profile-field">
          <span class="profile-field-label">Course / Dept</span>
          <span class="profile-field-value">${s.course ? `<span class="course-badge">${escapeHtml(s.course)}</span>` : 'Unassigned'}</span>
        </div>

        <div class="profile-field">
          <span class="profile-field-label">Enrollment Date</span>
          <span class="profile-field-value">${s.enrollment_date ? escapeHtml(s.enrollment_date) : 'N/A'}</span>
        </div>

        <div class="profile-field">
          <span class="profile-field-label">Email Address</span>
          <span class="profile-field-value">
            ${s.email ? `<a href="mailto:${escapeHtml(s.email)}">${escapeHtml(s.email)}</a>` : '<span style="color:var(--text-muted);">None provided</span>'}
          </span>
        </div>

        <div class="profile-field">
          <span class="profile-field-label">Phone Number</span>
          <span class="profile-field-value">
            ${s.phone ? `<a href="tel:${escapeHtml(s.phone)}">${escapeHtml(s.phone)}</a>` : '<span style="color:var(--text-muted);">None provided</span>'}
          </span>
        </div>

        <div class="profile-field full">
          <span class="profile-field-label">Address</span>
          <span class="profile-field-value">${s.address ? escapeHtml(s.address) : '<span style="color:var(--text-muted);">No address recorded</span>'}</span>
        </div>

        <div class="profile-field full">
          <span class="profile-field-label">Created At</span>
          <span class="profile-field-value" style="font-size:0.8rem; color:var(--text-muted);">
            ${new Date(s.created_at).toLocaleString()}
          </span>
        </div>
      `;

      profileFooterActions.innerHTML = `
        <button type="button" class="btn-danger" onclick="window.promptDeleteStudent('${escapeHtml(s.student_id)}', '${escapeHtml(s.name)}')">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="3 6 5 6 21 6"></polyline>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
          </svg>
          <span>Delete</span>
        </button>
        <div style="display:flex; gap:10px;">
          <button type="button" class="btn-secondary" onclick="document.getElementById('view-modal').classList.add('hidden')">Close</button>
          <button type="button" class="btn-primary" onclick="window.editStudent('${escapeHtml(s.student_id)}')">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
            </svg>
            <span>Edit Profile</span>
          </button>
        </div>
      `;

      viewModal.classList.remove('hidden');
    } catch (err) {
      showToast(err.message, 'error');
    }
  };

  // ----------------------------------------------------
  // Custom Delete Modal
  // ----------------------------------------------------
  window.promptDeleteStudent = function(studentId, studentName) {
    pendingDeleteId = studentId;
    deleteModalTitle.textContent = `Delete ${studentName || studentId}?`;
    deleteModalDesc.textContent = `Are you sure you want to delete ${studentName} (${studentId})? This record will be permanently deleted from SQLite storage.`;
    deleteModal.classList.remove('hidden');
  };

  async function executeConfirmedDelete() {
    if (!pendingDeleteId) return;
    const idToDelete = pendingDeleteId;

    try {
      const res = await fetch(`/students/${idToDelete}`, { method: 'DELETE' });
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || 'Delete failed');
      }

      deleteModal.classList.add('hidden');
      viewModal.classList.add('hidden');
      showToast(`Student ${idToDelete} permanently deleted`, 'success');
      pendingDeleteId = null;
      loadStudents();
      loadStats();
    } catch (err) {
      showToast(err.message, 'error');
    }
  }

  function closeModal() {
    studentModal.classList.add('hidden');
    editingStudentId = null;
    studentForm.reset();
  }

  // ----------------------------------------------------
  // Submit Add / Edit Form
  // ----------------------------------------------------
  async function handleFormSubmit(e) {
    e.preventDefault();
    modalError.classList.add('hidden');

    const emailVal = inpEmail.value.trim();
    const phoneVal = inpPhone.value.trim();

    if (!emailVal && !phoneVal) {
      modalError.textContent = "Validation error: At least one contact method (email or phone) is required.";
      modalError.classList.remove('hidden');
      return;
    }

    const payload = {
      name: inpName.value.trim(),
      date_of_birth: inpDob.value,
      email: emailVal || null,
      phone: phoneVal || null,
      course: inpCourse.value.trim() || null,
      address: inpAddress.value.trim() || null,
      enrollment_date: inpEnrollment.value || null,
    };

    try {
      let res;
      if (editingStudentId) {
        // Full update (PUT)
        res = await fetch(`/students/${editingStudentId}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
      } else {
        // Create (POST)
        payload.student_id = inpStudentId.value.trim();
        res = await fetch('/students', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
      }

      if (!res.ok) {
        const errData = await res.json();
        let errMsg = "An error occurred";
        if (errData.detail) {
          errMsg = Array.isArray(errData.detail)
            ? errData.detail.map(d => `${d.loc ? d.loc.join('.') + ': ' : ''}${d.msg}`).join(', ')
            : errData.detail;
        }
        throw new Error(errMsg);
      }

      showToast(editingStudentId ? 'Student updated successfully!' : 'Student created successfully!', 'success');
      closeModal();
      loadStudents();
      loadStats();
    } catch (err) {
      modalError.textContent = err.message;
      modalError.classList.remove('hidden');
    }
  }

  // ----------------------------------------------------
  // Ollama Status Check & AI Query Handler
  // ----------------------------------------------------
  async function checkOllamaStatus() {
    try {
      const res = await fetch('/ai/status');
      if (res.ok) {
        const statusData = await res.json();
        if (statusData.available) {
          ollamaStatusBadge.textContent = `Online (${statusData.default_model})`;
          ollamaStatusBadge.className = 'badge-status badge-online';
        } else {
          ollamaStatusBadge.textContent = 'Offline (Grounded Fallback Active)';
          ollamaStatusBadge.className = 'badge-status badge-offline';
        }
      }
    } catch (err) {
      ollamaStatusBadge.textContent = 'Offline (Grounded Fallback Active)';
      ollamaStatusBadge.className = 'badge-status badge-offline';
    }
  }

  async function handleAiQuery() {
    const question = aiQueryInput.value.trim();
    if (!question) return;

    aiLoader.classList.remove('hidden');
    aiResultPanel.classList.add('hidden');
    btnSubmitAi.disabled = true;

    try {
      const res = await fetch('/ai/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question })
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Failed to process AI query');
      }

      const data = await res.json();
      aiLoader.classList.add('hidden');
      aiResultPanel.classList.remove('hidden');

      aiSourceTag.textContent = data.source === 'ollama' ? `Source: Ollama (${data.model_used || 'LLM'})` : 'Source: Backend Grounded Analyzer';
      aiRecordsTag.textContent = `${data.records_referenced} database record(s) referenced`;
      aiAnswerText.textContent = data.answer;
    } catch (err) {
      aiLoader.classList.add('hidden');
      aiResultPanel.classList.remove('hidden');
      aiSourceTag.textContent = 'Error';
      aiRecordsTag.textContent = '0 records';
      aiAnswerText.textContent = `Query error: ${err.message}`;
    } finally {
      btnSubmitAi.disabled = false;
    }
  }

  // ----------------------------------------------------
  // Toast Helper
  // ----------------------------------------------------
  function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(8px)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 3200);
  }

  // ----------------------------------------------------
  // XSS Protection
  // ----------------------------------------------------
  function escapeHtml(str) {
    if (str === null || str === undefined) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }
});

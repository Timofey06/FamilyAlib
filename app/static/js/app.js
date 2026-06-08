const authTokenKey = 'booklistener_token';

function getToken() {
    const stored = localStorage.getItem(authTokenKey);
    if (stored && stored !== 'null' && stored !== 'undefined') {
        return stored;
    }
    const match = document.cookie.match(new RegExp('(^|;)\\s*' + authTokenKey + '\\s*=\\s*([^;]+)'));
    return match ? decodeURIComponent(match[2]) : null;
}

function setToken(token) {
    localStorage.setItem(authTokenKey, token);
    document.cookie = `${authTokenKey}=${encodeURIComponent(token)}; path=/; max-age=604800`;
}

function removeToken() {
    localStorage.removeItem(authTokenKey);
    localStorage.setItem(authTokenKey, 'null');
    document.cookie = `${authTokenKey}=; path=/; max-age=0`;
    document.cookie = `${authTokenKey}=; path=/; expires=Thu, 01 Jan 1970 00:00:00 UTC`;
}

async function validateAuthToken() {
    const token = getToken();
    if (!token) {
        removeToken();
        return false;
    }
    try {
        await apiFetch('/auth/me', { method: 'GET' });
        return true;
    } catch (err) {
        removeToken();
        return false;
    }
}

async function updateAuthUI() {
    const logoutButton = document.getElementById('logoutButton');
    const loginLink = document.getElementById('loginLink');
    const uploadLink = document.getElementById('uploadLink');
    const adminLink = document.getElementById('adminRegisterLink');
    const currentUserName = document.getElementById('currentUserName');
    
    let logged = await validateAuthToken();
    let isAdmin = false;
    let currentUser = null;
    
    if (logged) {
        try {
            currentUser = await apiFetch('/auth/me', { method: 'GET' });
            isAdmin = Boolean(currentUser.is_admin);
        } catch (err) {
            isAdmin = false;
            currentUser = null;
            logged = false;
        }
    }
    
    if (logoutButton) {
        if (logged) {
            logoutButton.classList.remove('hidden');
            logoutButton.style.display = 'inline-flex';
        } else {
            logoutButton.classList.add('hidden');
            logoutButton.style.display = 'none';
        }
    }
    
    if (loginLink) loginLink.classList.toggle('hidden', logged);
    if (uploadLink) uploadLink.classList.toggle('hidden', !logged);
    if (adminLink) adminLink.classList.toggle('hidden', !isAdmin);
    if (currentUserName) {
        currentUserName.classList.toggle('hidden', !logged);
        currentUserName.textContent = currentUser ? `Привет, ${currentUser.username}` : '';
    }
    
    if (logoutButton) {
        logoutButton.onclick = () => {
            removeToken();
            location.href = '/?t=' + Date.now();
        };
    }
}

function authHeaders() {
    const token = getToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
}

async function apiFetch(path, options = {}) {
    if (!(options.body instanceof FormData)) {
        options.headers = {
            'Content-Type': 'application/json',
            ...options.headers,
        };
        if (options.body) {
            options.body = JSON.stringify(options.body);
        }
    } else {
        options.headers = { ...options.headers };
    }
    if (!options.headers.Authorization) {
        options.headers = { ...options.headers, ...authHeaders() };
    }
    const response = await fetch(path, options);
    if (!response.ok) {
        const message = await response.text();
        throw new Error(message || 'Request failed');
    }
    return response.json();
}

function getFieldGroup(form, fieldName) {
    return form.querySelector(`.field-group[data-field="${fieldName}"]`);
}

function clearValidation(form) {
    const groups = form.querySelectorAll('.field-group');
    groups.forEach((group) => {
        group.classList.remove('field-error');
        const errorText = group.querySelector('.error-text');
        if (errorText) {
            errorText.textContent = '';
        }
    });
}

function setFieldError(form, fieldName, message) {
    const group = getFieldGroup(form, fieldName);
    if (!group) return;
    group.classList.add('field-error');
    const errorText = group.querySelector('.error-text');
    if (errorText) {
        errorText.textContent = message;
    }
}

function validateRequiredFields(form, fieldNames) {
    let valid = true;
    fieldNames.forEach((name) => {
        const input = form.elements[name];
        if (!input) return;
        const value = input.type === 'file' ? input.files.length : input.value.trim();
        if (!value) {
            setFieldError(form, name, 'Поле обязательно для заполнения');
            valid = false;
        }
    });
    return valid;
}

function getFormErrorMessage(error) {
    const text = error.message || String(error);
    if (/username.*taken|username.*exists|already.*taken/i.test(text)) {
        return 'Имя пользователя уже занято';
    }
    if (/password.*short|password.*invalid/i.test(text)) {
        return 'Пароль не соответствует требованиям';
    }
    return 'Ошибка выполнения запроса';
}

document.addEventListener('DOMContentLoaded', async () => {
    await updateAuthUI();
    const page = window.pageId;
    if (page === 'login') {
        const form = document.getElementById('loginForm');
        form.addEventListener('submit', async (event) => {
            event.preventDefault();
            clearValidation(form);
            const requiredFields = ['username', 'password'];
            if (!validateRequiredFields(form, requiredFields)) {
                return;
            }
            const data = new FormData(form);
            try {
                const result = await apiFetch('/auth/login', {
                    method: 'POST',
                    body: {
                        username: data.get('username'),
                        password: data.get('password'),
                    },
                });
                setToken(result.access_token);
                window.location.href = '/';
            } catch (err) {
                const message = getFormErrorMessage(err);
                alert(message);
            }
        });
    }
    if (page === 'users') {
        const form = document.getElementById('createUserForm');
        const existingUsernames = new Set();
        form.addEventListener('submit', async (event) => {
            event.preventDefault();
            clearValidation(form);
            const requiredFields = ['username', 'password', 'passwordConfirm'];
            if (!validateRequiredFields(form, requiredFields)) {
                return;
            }
            const data = new FormData(form);
            const username = data.get('username').trim();
            if (existingUsernames.has(username.toLowerCase())) {
                setFieldError(form, 'username', 'Имя пользователя уже занято');
                return;
            }
            const password = data.get('password');
            const passwordConfirm = data.get('passwordConfirm');
            if (password !== passwordConfirm) {
                setFieldError(form, 'passwordConfirm', 'Пароли не совпадают');
                return;
            }
            try {
                await apiFetch('/api/users', {
                    method: 'POST',
                    body: {
                        username: username,
                        password: password,
                    },
                });
                form.reset();
                await loadUsers();
            } catch (err) {
                const message = getFormErrorMessage(err);
                const errorText = String(err.message || err);
                if (/username.*already|already.*taken|exists/i.test(errorText)) {
                    setFieldError(form, 'username', message);
                } else {
                    alert(message);
                }
            }
        });
        function clearUserPasswordError(userId) {
            const error = document.getElementById(`passwordError-${userId}`);
            if (error) {
                error.textContent = '';
            }
        }

        function setUserPasswordError(userId, message) {
            const error = document.getElementById(`passwordError-${userId}`);
            if (error) {
                error.textContent = message;
            }
        }

        window.updatePassword = async (userId) => {
            clearUserPasswordError(userId);
            const input = document.getElementById(`passwordInput-${userId}`);
            if (!input) return;
            const password = input.value.trim();
            if (!password) {
                setUserPasswordError(userId, 'Введите новый пароль');
                return;
            }
            try {
                await apiFetch(`/api/users/${userId}/password`, {
                    method: 'PUT',
                    body: { password },
                });
                input.value = '';
            } catch (err) {
                const message = getFormErrorMessage(err);
                setUserPasswordError(userId, message);
            }
        };

        window.deleteUser = async (userId) => {
            try {
                await apiFetch(`/api/users/${userId}`, { method: 'DELETE' });
                await loadUsers();
            } catch (err) {
                alert('Ошибка удаления пользователя');
            }
        };
        const loadUsers = async () => {
            try {
                const users = await apiFetch('/api/users', { method: 'GET' });
                existingUsernames.clear();
                users.forEach((user) => existingUsernames.add(user.username.toLowerCase()));
                const currentUser = await apiFetch('/auth/me', { method: 'GET' });
                const wrapper = document.getElementById('usersTableWrapper');
                if (!users.length) {
                    wrapper.innerHTML = '<p>Пользователей пока нет.</p>';
                    return;
                }
                wrapper.innerHTML = `
                    <table class="users-table">
                        <thead>
                            <tr><th>ID</th><th>Имя пользователя</th><th>Админ</th><th>Дата создания</th><th>Пароль</th><th>Действия</th></tr>
                        </thead>
                        <tbody>
                            ${users
                                .map((user) => `
                                    <tr>
                                        <td>${user.id}</td>
                                        <td>${user.username}</td>
                                        <td>${user.is_admin ? 'Да' : 'Нет'}</td>
                                        <td>${new Date(user.created_at).toLocaleString()}</td>
                                        <td>
                                            <div class="password-change-row">
                                                <input id="passwordInput-${user.id}" type="password" placeholder="Новый пароль" />
                                                <button type="button" class="update-password-button" onclick="updatePassword(${user.id})">OK</button>
                                                <div id="passwordError-${user.id}" class="error-text"></div>
                                            </div>
                                        </td>
                                        <td>
                                            ${user.id === currentUser.id ? '<span class="disabled-action">Этот пользователь</span>' : `<button class="delete-user-button" onclick="deleteUser(${user.id})">Удалить</button>`}
                                        </td>
                                    </tr>
                                `)
                                .join('')}
                        </tbody>
                    </table>
                `;
            } catch (err) {
                document.getElementById('usersTableWrapper').innerHTML = '<p>Не удалось загрузить пользователей.</p>';
            }
        };
        await loadUsers();
    }
    if (page === 'upload') {
        const form = document.getElementById('uploadForm');
        const submitButton = form.querySelector('button[type="submit"]');
        form.addEventListener('submit', async (event) => {
            event.preventDefault();
            clearValidation(form);
            const requiredFields = ['title', 'author_name', 'cover', 'chapters'];
            if (!validateRequiredFields(form, requiredFields)) {
                return;
            }
            const data = new FormData(form);
            submitButton.disabled = true;
            const originalText = submitButton.textContent;
            submitButton.textContent = 'Загрузка...';
            const progressWrapper = document.getElementById('uploadProgressWrapper');
            const progressFill = document.getElementById('uploadProgressFill');
            const progressText = document.getElementById('uploadProgressText');
            try {
                const token = getToken();
                if (!token) throw new Error('Unauthorized');
                // ensure explicit boolean for show_to_all
                data.set('show_to_all', form.elements['show_to_all'] && form.elements['show_to_all'].checked ? 'true' : 'false');
                progressWrapper.classList.remove('hidden');
                const xhr = new XMLHttpRequest();
                xhr.open('POST', '/books');
                xhr.setRequestHeader('Authorization', `Bearer ${token}`);
                xhr.upload.onprogress = (e) => {
                    if (e.lengthComputable) {
                        const percent = Math.round((e.loaded / e.total) * 100);
                        progressFill.style.width = `${percent}%`;
                        progressText.textContent = `${percent}%`;
                    }
                };
                xhr.onload = () => {
                    if (xhr.status >= 200 && xhr.status < 300) {
                        window.location.href = '/';
                    } else {
                        const message = xhr.responseText || 'Upload failed';
                        alert(message);
                        submitButton.disabled = false;
                        submitButton.textContent = originalText;
                        progressWrapper.classList.add('hidden');
                    }
                };
                xhr.onerror = () => {
                    alert('Ошибка загрузки');
                    submitButton.disabled = false;
                    submitButton.textContent = originalText;
                    progressWrapper.classList.add('hidden');
                };
                xhr.send(data);
            } catch (err) {
                const message = getFormErrorMessage(err);
                alert(message);
                submitButton.disabled = false;
                submitButton.textContent = originalText;
            }
        });
    }
    if (page === 'index') {
        const searchInput = document.getElementById('searchInput');
        const booksSection = document.getElementById('booksSection');
        const continueSection = document.getElementById('continueSection');
        const loadBooks = async () => {
            const books = await apiFetch('/books');
            booksSection.innerHTML = books
                .map((book) => renderBookCard(book))
                .join('');
            continueSection.innerHTML = await renderContinueSection(books);
        };
        const fetchContinueBooks = async () => {
            const token = getToken();
            if (!token) return [];
            return apiFetch('/progress');
        };
        const renderContinueSection = async (books) => {
            try {
                const progress = await fetchContinueBooks();
                if (!progress.length) {
                    return '<p>Нет сохраненного прогресса.</p>';
                }
                const bookMap = Object.fromEntries(books.map((book) => [book.id, book]));
                return progress
                    .sort((a, b) => b.updated_at.localeCompare(a.updated_at))
                    .slice(0, 6)
                    .map((entry) => {
                        const book = bookMap[entry.book_id];
                        const progressPercent = entry.completion_percent || 0;
                        return renderBookCard(book, progressPercent);
                    })
                    .join('');
            } catch (err) {
                return '<p>Нет сохраненного прогресса.</p>';
            }
        };
        searchInput.addEventListener('input', async () => {
            const query = searchInput.value.toLowerCase();
            const books = await apiFetch('/books');
            const filtered = books.filter((book) =>
                book.title.toLowerCase().includes(query) || 
                book.author_name.toLowerCase().includes(query) ||
                (book.series_name && book.series_name.toLowerCase().includes(query))
            );
            booksSection.innerHTML = filtered.map((book) => renderBookCard(book)).join('');
        });
        loadBooks();
    }
    if (page === 'favorites') {
        loadFavorites();
    }
    if (page === 'book_detail') {
        loadBookDetail(window.currentBookId);
    }
});

function renderBookCard(book, progressPercent = null) {
    const progressHtml = progressPercent !== null && progressPercent > 0 
        ? `<div class="progress-bar"><div class="progress-fill" style="width: ${progressPercent}%"></div></div><p class="progress-text">${Math.round(progressPercent)}%</p>`
        : '';
    return `<div class="card book-card-clickable" onclick="window.location.href = '/book/${book.id}'" style="cursor: pointer;">
        <img src="/media/${book.cover_path}" alt="Обложка книги" />
        <h3>${book.title}</h3>
        <p>${book.author_name}</p>
        <p>${book.series_name || ''} ${book.series_order ? '№' + book.series_order : ''}</p>
        ${book.uploader_username ? `<p class="uploader-id">Загрузил: ${book.uploader_username}</p>` : ''}
        ${progressHtml}
    </div>`;
}

async function loadFavorites() {
    const section = document.getElementById('favoritesSection');
    try {
        const token = getToken();
        if (!token) throw new Error();
        const favorites = await apiFetch('/favorite', { method: 'GET' });
        if (!favorites.length) {
            section.innerHTML = '<p>Нет избранных книг.</p>';
            return;
        }
        const books = await apiFetch('/books');
        const bookMap = Object.fromEntries(books.map((book) => [book.id, book]));
        section.innerHTML = favorites
            .map((entry) => renderBookCard(bookMap[entry.book_id]))
            .join('');
    } catch (err) {
        section.innerHTML = '<p>Требуется вход для просмотра избранного.</p>';
    }
}

async function loadBookDetail(bookId) {
    const book = await apiFetch(`/books/${bookId}`);
    const bookCard = document.getElementById('bookCard');
    let isAdmin = false;
    let favoriteLabel = 'Избранное';
    try {
        currentUser = await apiFetch('/auth/me', { method: 'GET' });
        isAdmin = Boolean(currentUser.is_admin);
    } catch (err) {
        isAdmin = false;
        currentUser = null;
    }

    try {
        const favorites = await apiFetch('/favorite', { method: 'GET' });
        const isFavorite = favorites.some((entry) => entry.book_id === book.id);
        favoriteLabel = isFavorite ? 'Удалить из избранного' : 'Избранное';
    } catch (err) {
        favoriteLabel = 'Избранное';
    }

    bookCard.innerHTML = `
        <img src="/media/${book.cover_path}" alt="Обложка книги" />
        <h2>${book.title}</h2>
        <p>Автор: ${book.author_name}</p>
        <p>Серия: ${book.series_name || '—'}</p>
        <p>${book.description || ''}</p>
        <p>Общая длительность: ${formatTime(book.total_duration_seconds)}</p>
        <p>Загрузил: ${book.uploader_username || '—'}</p>
        <div class="detail-actions">
            <button id="favoriteButton" onclick="toggleFavorite(${book.id})">${favoriteLabel}</button>
            ${ (isAdmin || (currentUser && currentUser.id === book.uploader_id)) ? `<button class="edit-book-button" onclick="editBook(${book.id})">Изменить</button><button class="delete-book-button" onclick="deleteBook(${book.id})">Удалить книгу</button>` : '' }
        </div>
    `;
    const chapters = await apiFetch(`/books/${bookId}/chapters`);
    const chapterList = document.getElementById('chapterList');
    const player = document.getElementById('audioPlayer');
    let currentChapterId = null;

    const renderChapterList = () => {
        chapterList.innerHTML = chapters
            .map((chapter) => `
                <div class="chapter-item ${currentChapterId === chapter.id ? 'active' : ''}" 
                     onclick="playChapterAndUpdateUI(${bookId}, ${chapter.id}, '${chapter.file_path}')">
                    <div class="chapter-number">${chapter.chapter_number}</div>
                    <div class="chapter-info">
                        <div class="chapter-title">${chapter.title}</div>
                        <div class="chapter-duration">${formatTime(chapter.duration_seconds)}</div>
                    </div>
                </div>
            `)
            .join('');
    };

    renderChapterList();

    let progress = null;
    try {
        progress = await apiFetch(`/progress/${bookId}`);
    } catch {}
    
    const initialChapter = chapters.find((chapter) => chapter.id === progress?.current_chapter_id) || chapters[0];
    if (initialChapter) {
        currentChapterId = initialChapter.id;
        loadChapterForPlayback(initialChapter.file_path, progress?.current_position_seconds || 0);
        renderChapterList();
    }

    window.currentChapterId = currentChapterId;
    window.updateCurrentChapter = (chapterId) => {
        currentChapterId = chapterId;
        window.currentChapterId = chapterId;
        renderChapterList();
    };

    let heartbeat = null;
    player.addEventListener('timeupdate', () => {
        if (!player.paused && !player.seeking) {
            if (!heartbeat) {
                heartbeat = setInterval(() => saveProgress(bookId, chapters, player, book.total_duration_seconds), 3000);
            }
        } else if (heartbeat) {
            clearInterval(heartbeat);
            heartbeat = null;
            saveProgress(bookId, chapters, player, book.total_duration_seconds);
        }
    });
}

function formatTime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    if (hours > 0) {
        return `${hours}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

function loadChapterForPlayback(path, position = 0) {
    const player = document.getElementById('audioPlayer');
    player.src = `/media/${path}`;
    player.pause();
    
    const handleLoadedMetadata = () => {
        player.currentTime = position;
        player.removeEventListener('loadedmetadata', handleLoadedMetadata);
    };
    player.addEventListener('loadedmetadata', handleLoadedMetadata);
    player.load();
}

function playChapter(path, position = 0) {
    const player = document.getElementById('audioPlayer');
    player.src = `/media/${path}`;
    
    const handleLoadedMetadata = () => {
        player.currentTime = position;
        player.play();
        player.removeEventListener('loadedmetadata', handleLoadedMetadata);
    };
    player.addEventListener('loadedmetadata', handleLoadedMetadata);
    player.load();
}

function playChapterAndUpdateUI(bookId, chapterId, path) {
    if (window.updateCurrentChapter) {
        window.updateCurrentChapter(chapterId);
    }
    playChapter(path, 0);
}

async function saveProgress(bookId, chapters, player, totalDuration) {
    try {
        const currentFile = player.currentSrc.split('/').pop();
        const currentChapter = chapters.find((chapter) => chapter.file_path.endsWith(currentFile)) || chapters[0];
        
        let totalSeconds = 0;
        for (let i = 0; i < chapters.length; i++) {
            const chapter = chapters[i];
            if (chapter.file_path.endsWith(currentFile)) {
                totalSeconds += Math.floor(player.currentTime);
                break;
            }
            totalSeconds += chapter.duration_seconds || 0;
        }
        
        const completionPercent = totalDuration > 0 ? Math.floor((totalSeconds / totalDuration) * 100) : 0;
        
        await apiFetch('/progress', {
            method: 'POST',
            body: {
                book_id: bookId,
                current_chapter_id: currentChapter?.id || null,
                current_position_seconds: Math.floor(player.currentTime),
                completion_percent: completionPercent,
                is_finished: false,
            },
        });
    } catch (err) {
        console.warn('Progress save failed', err);
    }
}

async function toggleFavorite(bookId) {
    try {
        const result = await apiFetch(`/favorite/${bookId}`, { method: 'POST' });
        const button = document.getElementById('favoriteButton');
        if (button) {
            button.textContent = result.is_favorite ? 'Удалить из избранного' : 'В избранное';
        }
    } catch (err) {
        alert('Ошибка при обновлении избранного.');
    }
}

window.deleteBook = async (bookId) => {
    try {
        await apiFetch(`/books/${bookId}`, { method: 'DELETE' });
        window.location.href = '/';
    } catch (err) {
        alert('Ошибка удаления книги.');
    }
}

// Open edit modal and populate fields
window.editBook = async (bookId) => {
    try {
        const book = await apiFetch(`/books/${bookId}`);
        const modal = document.getElementById('editBookModal');
        const form = document.getElementById('editBookForm');
        form.elements['title'].value = book.title || '';
        form.elements['author_name'].value = book.author_name || '';
        form.elements['series_name'].value = book.series_name || '';
        form.elements['series_order'].value = book.series_order || '';
        form.elements['description'].value = book.description || '';
        form.elements['show_to_all'].checked = Boolean(book.show_to_all);
        modal.classList.remove('hidden');

        // cancel handler
        document.getElementById('cancelEditButton').onclick = () => {
            closeEditModal();
        };

        // submit handler
        form.onsubmit = async (e) => {
            e.preventDefault();
            clearValidation(form);
            const requiredFields = ['title', 'author_name'];
            if (!validateRequiredFields(form, requiredFields)) return;
            const data = new FormData();
            data.append('title', form.elements['title'].value.trim());
            data.append('author_name', form.elements['author_name'].value.trim());
            const seriesNameValue = form.elements['series_name'].value.trim();
            if (seriesNameValue) {
                data.append('series_name', seriesNameValue);
            }
            const seriesOrderValue = form.elements['series_order'].value;
            if (seriesOrderValue) {
                data.append('series_order', seriesOrderValue);
            }
            data.append('description', form.elements['description'].value.trim() || '');
            data.append('show_to_all', form.elements['show_to_all'].checked ? 'true' : 'false');
            const coverFile = form.elements['cover'].files[0];
            if (coverFile) {
                data.append('cover', coverFile);
            }
            const progressWrapper = document.getElementById('editProgressWrapper');
            const progressFill = document.getElementById('editProgressFill');
            const progressText = document.getElementById('editProgressText');
            progressWrapper.classList.remove('hidden');
            const xhr = new XMLHttpRequest();
            const token = getToken();
            xhr.open('PUT', `/books/${bookId}`);
            xhr.setRequestHeader('Authorization', `Bearer ${token}`);
            xhr.upload.onprogress = (event) => {
                if (event.lengthComputable) {
                    const percent = Math.round((event.loaded / event.total) * 100);
                    progressFill.style.width = `${percent}%`;
                    progressText.textContent = `${percent}%`;
                }
            };
            xhr.onload = () => {
                if (xhr.status >= 200 && xhr.status < 300) {
                    closeEditModal();
                    window.location.reload();
                } else {
                    const message = xhr.responseText || 'Ошибка изменения книги.';
                    alert(message);
                    progressWrapper.classList.add('hidden');
                }
            };
            xhr.onerror = () => {
                alert('Ошибка изменения книги.');
                progressWrapper.classList.add('hidden');
            };
            xhr.send(data);
        };
    } catch (err) {
        alert('Ошибка получения данных книги.');
    }
};

function closeEditModal() {
    const modal = document.getElementById('editBookModal');
    const form = document.getElementById('editBookForm');
    if (form) form.reset();
    if (modal) modal.classList.add('hidden');
}

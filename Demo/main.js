// WebSocket Connection
const ws = new WebSocket('ws://localhost:8080');

ws.onopen = function() {
  console.log('Connected to WebSocket server');
};

ws.onclose = function() {
  console.log('Disconnected from WebSocket server');
};

ws.onerror = function(error) {
  console.error('WebSocket error:', error);
};

// Timeline Functionality
document.addEventListener('DOMContentLoaded', function() {
  const timelineContainer = document.querySelector('.timeline-container');
  const timelineWrapper = document.querySelector('.timeline-wrapper');
  const timelineScroll = document.querySelector('.timeline-scroll');
  const timelineGrid = document.querySelector('.timeline-grid');
  const timelineToday = document.querySelector('.timeline-today');
  const zoomButtons = document.querySelectorAll('.timeline-controls button');

  // Initialize timeline
  function initTimeline() {
    // Set today's marker position
    const today = new Date();
    const startDate = new Date(today.getFullYear(), today.getMonth(), 1);
    const endDate = new Date(today.getFullYear(), today.getMonth() + 1, 0);
    const totalDays = endDate.getDate();
    const todayPosition = ((today.getDate() - 1) / (totalDays - 1)) * 100;
    timelineToday.style.left = `${todayPosition}%`;

    // Create grid lines
    for (let i = 0; i < 30; i++) {
      const line = document.createElement('div');
      line.className = 'timeline-grid-line';
      timelineGrid.appendChild(line);
    }

    // Create sample tasks
    createTimelineTask('Power Core Maintenance', '2024-03-10', '2024-03-15', 'in-progress');
    createTimelineTask('Shield Generator Upgrade', '2024-03-12', '2024-03-18', 'blocked');
    createTimelineTask('Weapon System Testing', '2024-03-20', '2024-03-25', 'completed');
  }

  // Create a timeline task
  function createTimelineTask(name, startDate, endDate, status) {
    const task = document.createElement('div');
    task.className = `timeline-task ${status}`;
    task.setAttribute('data-task-id', name.toLowerCase().replace(/\s+/g, '-'));
    task.setAttribute('draggable', 'true');

    const taskName = document.createElement('div');
    taskName.className = 'task-name';
    taskName.textContent = name;
    task.appendChild(taskName);

    const taskDates = document.createElement('div');
    taskDates.className = 'task-dates';
    taskDates.textContent = `${formatDate(startDate)} - ${formatDate(endDate)}`;
    task.appendChild(taskDates);

    // Position the task
    const start = new Date(startDate);
    const end = new Date(endDate);
    const today = new Date();
    const monthStart = new Date(today.getFullYear(), today.getMonth(), 1);
    const monthEnd = new Date(today.getFullYear(), today.getMonth() + 1, 0);
    const totalDays = monthEnd.getDate();
    
    const startPosition = ((start.getDate() - 1) / (totalDays - 1)) * 100;
    const endPosition = ((end.getDate() - 1) / (totalDays - 1)) * 100;
    const width = endPosition - startPosition;

    task.style.left = `${startPosition}%`;
    task.style.width = `${width}%`;

    timelineScroll.appendChild(task);

    // Add drag functionality
    task.addEventListener('dragstart', function(e) {
      this.classList.add('dragging');
      e.dataTransfer.setData('text/plain', this.dataset.taskId);
    });

    task.addEventListener('dragend', function() {
      this.classList.remove('dragging');
    });

    // Add double-click to open details
    task.addEventListener('dblclick', function() {
      openIssueDetails(this.dataset.taskId);
    });
  }

  // Format date for display
  function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  }

  // Zoom controls
  zoomButtons.forEach(button => {
    button.addEventListener('click', function() {
      zoomButtons.forEach(btn => btn.classList.remove('active'));
      this.classList.add('active');
      
      const scale = this.dataset.zoom;
      timelineWrapper.style.transform = `scaleX(${scale})`;
    });
  });

  // Initialize timeline
  initTimeline();
});

// Kanban Board Functionality
document.addEventListener('DOMContentLoaded', function() {
  const kanbanBoard = document.querySelector('.kanban-board');
  const columns = document.querySelectorAll('.kanban-column');
  const cards = document.querySelectorAll('.kanban-card');

  // Make cards draggable
  cards.forEach(card => {
    card.setAttribute('draggable', 'true');
    card.addEventListener('dragstart', handleDragStart);
    card.addEventListener('dragend', handleDragEnd);
  });

  // Make columns droppable
  columns.forEach(column => {
    column.addEventListener('dragover', handleDragOver);
    column.addEventListener('dragleave', handleDragLeave);
    column.addEventListener('drop', handleDrop);
  });

  // Drag start handler
  function handleDragStart(e) {
    this.classList.add('dragging');
    e.dataTransfer.setData('text/plain', this.dataset.cardId);
    
    // Create drop targets
    columns.forEach(column => {
      const dropTarget = document.createElement('div');
      dropTarget.className = 'drop-target';
      column.querySelector('.column-content').appendChild(dropTarget);
    });
  }

  // Drag end handler
  function handleDragEnd() {
    this.classList.remove('dragging');
    
    // Remove drop targets
    document.querySelectorAll('.drop-target').forEach(target => {
      target.remove();
    });
  }

  // Drag over handler
  function handleDragOver(e) {
    e.preventDefault();
    this.classList.add('drag-over');
    
    const draggingCard = document.querySelector('.kanban-card.dragging');
    const dropTargets = this.querySelectorAll('.drop-target');
    
    dropTargets.forEach(target => {
      const rect = target.getBoundingClientRect();
      const y = e.clientY - rect.top;
      
      if (y < rect.height / 2) {
        target.classList.add('valid');
      } else {
        target.classList.remove('valid');
      }
    });
  }

  // Drag leave handler
  function handleDragLeave() {
    this.classList.remove('drag-over');
  }

  // Drop handler
  function handleDrop(e) {
    e.preventDefault();
    this.classList.remove('drag-over');
    
    const cardId = e.dataTransfer.getData('text/plain');
    const card = document.querySelector(`[data-card-id="${cardId}"]`);
    const dropTarget = this.querySelector('.drop-target.valid');
    
    if (dropTarget) {
      dropTarget.parentNode.insertBefore(card, dropTarget);
    } else {
      this.querySelector('.column-content').appendChild(card);
    }
    
    // Update column counts
    updateColumnCounts();
    
    // Send update to server
    ws.send(JSON.stringify({
      type: 'card_moved',
      cardId: cardId,
      newColumn: this.dataset.column
    }));
    
    // Show success toast
    showToast(`Task ${cardId} moved to ${this.dataset.column}`, 'success');
  }

  // Update column counts
  function updateColumnCounts() {
    columns.forEach(column => {
      const count = column.querySelectorAll('.kanban-card').length;
      column.querySelector('.column-count').textContent = count;
    });
  }

  // Card actions
  cards.forEach(card => {
    const actions = card.querySelector('.card-actions');
    const editButton = actions.querySelector('.action-button:first-child');
    const commentButton = actions.querySelector('.comment-count');
    const moreButton = actions.querySelector('.more-menu');
    
    // Edit button
    editButton.addEventListener('click', function(e) {
      e.stopPropagation();
      openIssueDetails(card.dataset.cardId);
    });
    
    // Comment button
    commentButton.addEventListener('click', function(e) {
      e.stopPropagation();
      openIssueDetails(card.dataset.cardId, 'comments');
    });
    
    // More menu
    moreButton.addEventListener('click', function(e) {
      e.stopPropagation();
      const menu = this.querySelector('.more-menu-content');
      menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
    });
  });
});

// Toast Notification System
function showToast(message, type = 'info', duration = 3000) {
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.setAttribute('role', 'alert');
  toast.setAttribute('aria-live', 'polite');
  toast.textContent = message;
  
  document.body.appendChild(toast);
  
  // Remove toast after duration
  setTimeout(() => {
    toast.style.animation = 'slideOut 0.3s ease-out forwards';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

// Issue Detail Drawer
function openIssueDetails(issueId, tab = 'summary') {
  const drawer = document.querySelector('.issue-drawer');
  const tabButtons = document.querySelectorAll('.tab-button');
  const tabContents = document.querySelectorAll('.tab-content');
  
  // Show drawer
  drawer.classList.add('active');
  
  // Set active tab
  tabButtons.forEach(button => {
    button.classList.toggle('active', button.dataset.tab === tab);
  });
  
  tabContents.forEach(content => {
    content.classList.toggle('active', content.id === tab);
  });
  
  // Load issue details
  loadIssueDetails(issueId);
}

function loadIssueDetails(issueId) {
  // This would be replaced with actual data fetching
  console.log('Loading details for issue:', issueId);
}

// WebSocket Message Handler
ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  
  switch (data.type) {
    case 'card_moved':
      updateKanbanCard(data.cardId, data.newColumn);
      showToast(`Task ${data.cardId} moved to ${data.newColumn}`, 'success');
      break;
    case 'status_changed':
      updateIssueStatus(data.issueId, data.newStatus);
      showToast(`Status updated for ${data.issueId}`, 'info');
      break;
    case 'comment_added':
      addNewComment(data.issueId, data.comment);
      showToast(`New comment on ${data.issueId}`, 'info');
      break;
    case 'error':
      showToast(data.message, 'error');
      break;
  }
};

// Update Kanban card
function updateKanbanCard(cardId, newColumn) {
  const card = document.querySelector(`[data-card-id="${cardId}"]`);
  const column = document.querySelector(`[data-column="${newColumn}"]`);
  
  if (card && column) {
    column.querySelector('.column-content').appendChild(card);
    updateColumnCounts();
  }
}

// Update issue status
function updateIssueStatus(issueId, newStatus) {
  const card = document.querySelector(`[data-card-id="${issueId}"]`);
  if (card) {
    card.className = `kanban-card ${newStatus}`;
  }
}

// Add new comment
function addNewComment(issueId, comment) {
  const commentsSection = document.querySelector(`#comments[data-issue-id="${issueId}"]`);
  if (commentsSection) {
    const commentElement = document.createElement('div');
    commentElement.className = 'comment';
    commentElement.innerHTML = `
      <div class="comment-header">
        <div class="comment-author">
          <div class="assignee-avatar">${comment.author.charAt(0)}</div>
          <span>${comment.author}</span>
        </div>
        <span class="comment-time">${formatTimeAgo(comment.timestamp)}</span>
      </div>
      <div class="comment-content">
        <p>${comment.content}</p>
      </div>
    `;
    commentsSection.appendChild(commentElement);
  }
}

// Format time ago
function formatTimeAgo(timestamp) {
  const now = new Date();
  const date = new Date(timestamp);
  const diff = now - date;
  
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);
  
  if (days > 0) return `${days} days ago`;
  if (hours > 0) return `${hours} hours ago`;
  if (minutes > 0) return `${minutes} minutes ago`;
  return 'just now';
} 
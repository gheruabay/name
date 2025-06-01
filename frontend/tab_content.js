function openTab(tabId, event) {
  const tabContents = document.getElementsByClassName('tab-content');
  for (let i = 0; i < tabContents.length; i++) {
    tabContents[i].classList.remove('active');
  }

  const tabButtons = document.getElementsByClassName('tab-btn');
  for (let i = 0; i < tabButtons.length; i++) {
    tabButtons[i].classList.remove('active');
  }

  const tabToShow = document.getElementById(tabId);
  if (tabToShow) {
    tabToShow.classList.add('active');
  }

  if (event && event.currentTarget) {
    event.currentTarget.classList.add('active');
  }
}

function initTabs() {
  // Gán sự kiện click cho các tab button
  const tabButtons = document.getElementsByClassName('tab-btn');
  for (let i = 0; i < tabButtons.length; i++) {
    tabButtons[i].addEventListener('click', function(e) {
      const tabId = this.getAttribute('data-tab');
      if (tabId) {
        openTab(tabId, e);
      }
    });
  }

  // Mở tab đầu tiên mặc định
  const defaultTab = document.querySelector('.tab-btn.active');
  if (defaultTab) {
    const defaultTabId = defaultTab.getAttribute('data-tab');
    if (defaultTabId) {
      openTab(defaultTabId, { currentTarget: defaultTab });
    }
  }
}

document.addEventListener('DOMContentLoaded', initTabs);

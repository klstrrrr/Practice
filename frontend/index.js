const authPanel = document.querySelector("#auth-panel");
const appPanel = document.querySelector("#app-panel");
const authForm = document.querySelector("#auth-form");
const authTitle = document.querySelector("#auth-title");
const authDescription = document.querySelector("#auth-description");
const authSubmit = document.querySelector("#auth-submit");
const authMessage = document.querySelector("#auth-message");
const loginTab = document.querySelector("#login-tab");
const registerTab = document.querySelector("#register-tab");
const passwordInput = document.querySelector("#password");
const taskForm = document.querySelector("#task-form");
const taskList = document.querySelector("#task-list");
const taskCount = document.querySelector("#task-count");
const taskMessage = document.querySelector("#task-message");
const listMessage = document.querySelector("#list-message");
const statusFilter = document.querySelector("#status-filter");

let authMode = "login";
let tasks = [];

async function request(path, options = {}) {
  const response = await fetch(path, {
    credentials: "same-origin",
    ...options,
    headers: {
      ...(options.body ? { "Content-Type": "application/json" } : {}),
      ...options.headers,
    },
  });

  const result = response.status === 204 ? null : await response.json();
  if (!response.ok) {
    throw new Error(result?.error || "Something went wrong. Please try again.");
  }
  return result;
}

function setMessage(element, text) {
  element.textContent = text;
}

function showAuthenticatedView() {
  authPanel.classList.add("hidden");
  appPanel.classList.remove("hidden");
}

function showAuthView() {
  appPanel.classList.add("hidden");
  authPanel.classList.remove("hidden");
}

function setAuthMode(mode) {
  authMode = mode;
  const registering = mode === "register";
  loginTab.classList.toggle("active", !registering);
  registerTab.classList.toggle("active", registering);
  loginTab.setAttribute("aria-selected", String(!registering));
  registerTab.setAttribute("aria-selected", String(registering));
  authTitle.textContent = registering ? "Create your account" : "Welcome back";
  authDescription.textContent = registering
    ? "A fresh start is just a few details away."
    : "Sign in to pick up where you left off.";
  authSubmit.textContent = registering ? "Create account" : "Sign in";
  passwordInput.autocomplete = registering ? "new-password" : "current-password";
  setMessage(authMessage, "");
}

async function loadTasks() {
  setMessage(listMessage, "");
  tasks = await request("/api/tasks");
  renderTasks();
}

function renderTasks() {
  const filter = statusFilter.value;
  const visibleTasks = filter === "All"
    ? tasks
    : tasks.filter((task) => task.status === filter);

  taskCount.textContent = String(tasks.length);
  taskList.replaceChildren();

  if (visibleTasks.length === 0) {
    const emptyState = document.createElement("li");
    emptyState.className = "empty-state";
    emptyState.textContent = tasks.length === 0
      ? "Your list is clear. Add a task above to get started."
      : `No ${filter.toLowerCase()} tasks right now.`;
    taskList.append(emptyState);
    return;
  }

  for (const task of visibleTasks) {
    const item = document.createElement("li");
    item.className = `task-card${task.status === "Done" ? " is-done" : ""}`;

    const content = document.createElement("div");
    const title = document.createElement("p");
    title.className = "task-title";
    title.textContent = task.title;
    content.append(title);
    if (task.description) {
      const description = document.createElement("p");
      description.className = "task-description";
      description.textContent = task.description;
      content.append(description);
    }

    const actions = document.createElement("div");
    actions.className = "task-actions";
    const status = document.createElement("select");
    status.setAttribute("aria-label", `Status for ${task.title}`);
    for (const optionText of ["To Do", "In Progress", "Done"]) {
      const option = document.createElement("option");
      option.value = optionText;
      option.textContent = optionText;
      option.selected = task.status === optionText;
      status.append(option);
    }
    status.addEventListener("change", () => updateTaskStatus(task, status.value, status));

    const deleteButton = document.createElement("button");
    deleteButton.className = "delete-button";
    deleteButton.type = "button";
    deleteButton.setAttribute("aria-label", `Delete ${task.title}`);
    deleteButton.textContent = "×";
    deleteButton.addEventListener("click", () => removeTask(task.id, deleteButton));

    actions.append(status, deleteButton);
    item.append(content, actions);
    taskList.append(item);
  }
}

async function updateTaskStatus(task, status, control) {
  control.disabled = true;
  setMessage(listMessage, "");
  try {
    const updatedTask = await request(`/api/tasks/${task.id}`, {
      method: "PUT",
      body: JSON.stringify({ status }),
    });
    tasks = tasks.map((item) => item.id === updatedTask.id ? updatedTask : item);
    renderTasks();
  } catch (error) {
    setMessage(listMessage, error.message);
    control.value = task.status;
    control.disabled = false;
  }
}

async function removeTask(taskId, control) {
  control.disabled = true;
  setMessage(listMessage, "");
  try {
    await request(`/api/tasks/${taskId}`, { method: "DELETE" });
    tasks = tasks.filter((task) => task.id !== taskId);
    renderTasks();
  } catch (error) {
    setMessage(listMessage, error.message);
    control.disabled = false;
  }
}

loginTab.addEventListener("click", () => setAuthMode("login"));
registerTab.addEventListener("click", () => setAuthMode("register"));
statusFilter.addEventListener("change", renderTasks);

authForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  authSubmit.disabled = true;
  setMessage(authMessage, "");
  const formData = new FormData(authForm);
  const credentials = {
    username: formData.get("username").trim(),
    password: formData.get("password"),
  };

  try {
    if (authMode === "register") {
      await request("/api/register", {
        method: "POST",
        body: JSON.stringify(credentials),
      });
    }
    await request("/api/login", {
      method: "POST",
      body: JSON.stringify(credentials),
    });
    showAuthenticatedView();
    authForm.reset();
    await loadTasks();
  } catch (error) {
    if (authMode === "register" && error.message === "Username is already registered") {
      setMessage(authMessage, "That username is taken. Try signing in instead.");
    } else {
      setMessage(authMessage, error.message);
    }
  } finally {
    authSubmit.disabled = false;
  }
});

taskForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const submitButton = taskForm.querySelector('button[type="submit"]');
  submitButton.disabled = true;
  setMessage(taskMessage, "");
  const formData = new FormData(taskForm);

  try {
    const task = await request("/api/tasks", {
      method: "POST",
      body: JSON.stringify({
        title: formData.get("title").trim(),
        description: formData.get("description").trim() || null,
      }),
    });
    tasks.unshift(task);
    taskForm.reset();
    renderTasks();
    document.querySelector("#task-title").focus();
  } catch (error) {
    setMessage(taskMessage, error.message);
  } finally {
    submitButton.disabled = false;
  }
});

document.querySelector("#logout-button").addEventListener("click", async (event) => {
  const button = event.currentTarget;
  button.disabled = true;
  setMessage(listMessage, "");
  try {
    await request("/api/logout", { method: "POST" });
    tasks = [];
    taskForm.reset();
    showAuthView();
    setAuthMode("login");
  } catch (error) {
    setMessage(listMessage, error.message);
  } finally {
    button.disabled = false;
  }
});

request("/api/tasks")
  .then((userTasks) => {
    tasks = userTasks;
    showAuthenticatedView();
    renderTasks();
  })
  .catch((error) => {
    showAuthView();
    if (!error.message.includes("Authentication required")) {
      setMessage(authMessage, error.message);
    }
  });
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Custom metric to track failure rate
let failureRate = new Rate('check_failure_rate');

export const options = {
  // Define test execution stages
  stages: [
    { duration: '2m', target: 50 },    // Ramp up to 50 users over 2 minutes
    { duration: '5m', target: 50 },    // Stay at 50 users for 5 minutes
    { duration: '2m', target: 100 },   // Ramp up to 100 users over 2 minutes
    { duration: '5m', target: 100 },   // Stay at 100 users for 5 minutes
    { duration: '2m', target: 0 },     // Ramp down to 0 users
  ],
  thresholds: {
    // Define acceptable performance thresholds
    'http_req_duration': ['p(95)<500'], // 95% of requests must complete within 500ms
    'check_failure_rate': ['rate<0.1'], // Failure rate must be less than 10%
    'http_req_failed': ['rate<0.05'],   // Less than 5% of requests should fail
  },
};

// Get API base URL from environment or use default
const API_BASE = __ENV.API_URL || 'http://localhost:8000';

// Generate random user ID for testing
function getRandomUserId() {
  return Math.random().toString(36).substring(2, 15);
}

// Generate random task data
function generateRandomTask() {
  const titles = [
    'Complete project proposal',
    'Review quarterly reports',
    'Schedule team meeting',
    'Update documentation',
    'Fix critical bug',
    'Prepare presentation',
    'Research new technologies',
    'Code review',
    'Deploy to staging',
    'Client follow-up'
  ];

  return {
    title: `${titles[Math.floor(Math.random() * titles.length)]} ${Math.random().toString(36).substring(7)}`,
    description: 'Automated load test task',
    status: 'pending',
    priority: ['low', 'medium', 'high'][Math.floor(Math.random() * 3)],
    due_date: new Date(Date.now() + Math.floor(Math.random() * 7) * 24 * 60 * 60 * 1000).toISOString(),
  };
}

export default function() {
  // Create a new task
  const createTaskPayload = generateRandomTask();
  const createTaskParams = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  const createTaskRes = http.post(`${API_BASE}/api/tasks`, JSON.stringify(createTaskPayload), createTaskParams);

  check(createTaskRes, {
    'create task status is 200': (r) => r.status === 200,
    'create task has valid response': (r) => {
      try {
        const response = r.json();
        return response.hasOwnProperty('id') && response.title === createTaskPayload.title;
      } catch (e) {
        return false;
      }
    }
  }) || failureRate.add(1);

  // Pause briefly between operations
  sleep(1);

  // List tasks
  const listTasksRes = http.get(`${API_BASE}/api/tasks`);

  check(listTasksRes, {
    'list tasks status is 200': (r) => r.status === 200,
    'list tasks returns array': (r) => {
      try {
        const response = r.json();
        return Array.isArray(response);
      } catch (e) {
        return false;
      }
    }
  }) || failureRate.add(1);

  // Pause between operations
  sleep(1);

  // If we successfully created a task, try to update it
  if (createTaskRes.status === 200) {
    try {
      const taskId = createTaskRes.json().id;

      const updateTaskPayload = {
        title: `Updated: ${createTaskPayload.title}`,
        status: 'completed',
      };

      const updateTaskRes = http.put(`${API_BASE}/api/tasks/${taskId}`, JSON.stringify(updateTaskPayload), createTaskParams);

      check(updateTaskRes, {
        'update task status is 200': (r) => r.status === 200,
        'update task has correct status': (r) => {
          try {
            const response = r.json();
            return response.status === 'completed';
          } catch (e) {
            return false;
          }
        }
      }) || failureRate.add(1);
    } catch (e) {
      failureRate.add(1);
    }
  }

  // Pause between virtual user iterations
  sleep(2);
}

// Optional: Setup and teardown functions
export function setup() {
  console.log('Starting load test...');
  return { setup_value: 'test' };
}

export function teardown(data) {
  console.log('Load test completed.');
}
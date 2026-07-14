<template>
  <div class="admin-dashboard">
    <h3 class="mb-4">Admin Dashboard</h3>
    
    <div class="row mb-4">
      <div class="col-md-2" v-for="card in cards" :key="card.label">
        <div class="card text-center border-primary h-100">
          <div class="card-body">
            <h6 class="card-title text-secondary">{{ card.label }}</h6>
            <p class="display-6 mb-0">{{ card.value }}</p>
          </div>
        </div>
      </div>
    </div>

    <div class="row gy-4 mb-4">
      <div class="col-lg-6">
        <div class="card h-100">
          <div class="card-header d-flex justify-content-between align-items-center">
            <span>Drive Status Overview</span>
            <span class="text-muted small">Pending / Approved / Rejected</span>
          </div>
          <div class="card-body">
            <div class="row align-items-center">
              <div class="col-md-8">
                <canvas ref="chartCanvas" height="220"></canvas>
              </div>
              <div class="col-md-4">
                <ul class="list-unstyled mb-0">
                  <li class="mb-2"><span class="badge bg-warning me-2">Pending</span>{{ chartCounts.pending }}</li>
                  <li class="mb-2"><span class="badge bg-success me-2">Approved</span>{{ chartCounts.approved }}</li>
                  <li><span class="badge bg-danger me-2">Rejected</span>{{ chartCounts.rejected }}</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="col-lg-6">
        <div class="card h-100">
          <div class="card-header d-flex justify-content-between align-items-center">
            <span>Company Registration Overview</span>
            <span class="text-muted small">Pending / Approved / Rejected</span>
          </div>
          <div class="card-body">
            <div class="row align-items-center">
              <div class="col-md-8">
                <canvas ref="companyChartCanvas" height="220"></canvas>
              </div>
              <div class="col-md-4">
                <ul class="list-unstyled mb-0">
                  <li class="mb-2"><span class="badge bg-warning me-2">Pending</span>{{ companyChartCounts.pending }}</li>
                  <li class="mb-2"><span class="badge bg-success me-2">Approved</span>{{ companyChartCounts.approved }}</li>
                  <li><span class="badge bg-danger me-2">Rejected</span>{{ companyChartCounts.rejected }}</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="row gy-4">
      <div class="col-md-6">
        <div class="card mb-4">
          <div class="card-header">Operations</div>
          <div class="card-body">
            <div class="d-flex flex-wrap gap-2 mb-3">
              <button class="btn btn-outline-primary" @click="generateReport">Generate Monthly Report</button>
              <button class="btn btn-outline-secondary" @click="triggerReminders">Trigger Daily Reminders</button>
            </div>
            <div v-if="operationsMessage" class="alert alert-info py-2 mb-0">{{ operationsMessage }}</div>
          </div>
        </div>
        <div class="card mb-4">
          <div class="card-header">Pending Company Approvals</div>
          <div class="card-body">
            <div class="input-group mb-3">
              <input v-model="pendingCompanyQuery" class="form-control" placeholder="Search all company fields" />
            </div>
            <div class="table-responsive">
              <table class="table mb-0">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Status</th>
                    <th class="text-end">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="company in filteredPendingCompanies" :key="company.company_id">
                    <td>{{ company.name }}</td>
                    <td>{{ company.email }}</td>
                    <td>{{ company.approved ? 'Approved' : 'Pending' }}</td>
                    <td class="text-end">
                      <button class="btn btn-sm btn-outline-primary me-1" @click="lookUser(company, 'company')">Look</button>
                      <button class="btn btn-sm btn-success me-1" @click="approveCompany(company.company_id)">Approve</button>
                      <button class="btn btn-sm btn-danger" @click="rejectCompany(company.company_id)">Reject</button>
                    </td>
                  </tr>
                  <tr v-if="filteredPendingCompanies.length === 0">
                    <td colspan="4" class="text-center py-3">No pending companies.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div class="card mb-4">
          <div class="card-header d-flex justify-content-between align-items-center">
            <span>Placement Drives</span>
            <div class="btn-group btn-group-sm" role="group">
              <button v-for="mode in driveModes" :key="mode" class="btn" :class="mode === activeDriveMode ? 'btn-primary' : 'btn-outline-secondary'" @click="activeDriveMode = mode">
                {{ mode }}
              </button>
            </div>
          </div>
          <div class="card-body p-0">
            <table class="table mb-0">
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Company</th>
                  <th>Created</th>
                  <th class="text-end">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="drive in filteredDrives" :key="drive.drive_id">
                  <td>{{ drive.title }}</td>
                  <td>{{ drive.company_name || 'Unknown' }}</td>
                  <td>{{ formatDate(drive.created_at) }}</td>
                  <td class="text-end">
                    <button class="btn btn-sm btn-outline-primary" @click="openDriveDetails(drive)">Details</button>
                  </td>
                </tr>
                <tr v-if="filteredDrives.length === 0">
                  <td colspan="4" class="text-center py-3">No {{ activeDriveMode === 'All' ? 'drives' : activeDriveMode.toLowerCase() + ' drives' }}.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div v-if="selectedDrive" class="card mb-4 border-primary">
          <div class="card-header">Drive Review</div>
          <div class="card-body">
            <div class="row g-4">
              <div class="col-md-5">
                <h6 class="text-uppercase text-secondary">Company Profile</h6>
                <p><strong>Name:</strong> {{ selectedDrive.company_name || 'Unknown' }}</p>
                <p><strong>Status:</strong> {{ selectedDrive.company?.approved ? 'Approved' : 'Pending Approval' }}</p>
                <p><strong>HR Contact:</strong> {{ selectedDrive.company?.hr_contact || '—' }}</p>
                <p><strong>Website:</strong> {{ selectedDrive.company?.website || '—' }}</p>
              </div>
              <div class="col-md-7">
                <h6 class="text-uppercase text-secondary">Drive Details</h6>
                <p><strong>Title:</strong> {{ selectedDrive.title }}</p>
                <p><strong>Description:</strong> {{ selectedDrive.description || '—' }}</p>
                <p><strong>Eligibility:</strong> {{ selectedDrive.eligibility || '—' }}</p>
                <p><strong>Drive Date:</strong> {{ formatDate(selectedDrive.drive_date) }}</p>
                <p><strong>Created:</strong> {{ formatDate(selectedDrive.created_at) }}</p>
                <p><strong>Application Deadline:</strong> {{ formatDate(selectedDrive.application_deadline) }}</p>
              </div>
            </div>

            <div class="mt-3">
              <label class="form-label">Set status</label>
              <div class="d-flex flex-wrap gap-3">
                <div v-for="mode in driveModes" :key="mode" class="form-check">
                  <input class="form-check-input" type="radio" :id="`drive-status-${mode}`" :value="mode" v-model="selectedDriveStatus" />
                  <label class="form-check-label" :for="`drive-status-${mode}`">{{ mode }}</label>
                </div>
              </div>
            </div>

            <div class="mt-4">
              <h6 class="mb-3">Applicants</h6>
              <div v-if="driveReviewApplicants.length" class="table-responsive">
                <table class="table table-sm mb-0">
                  <thead>
                    <tr>
                      <th>Name</th>
                      <th>Email</th>
                      <th>Status</th>
                      <th class="text-end">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="applicant in driveReviewApplicants" :key="applicant.application_id">
                      <td>{{ applicant.student_name || 'Unknown' }}</td>
                      <td>{{ applicant.student_email || '—' }}</td>
                      <td>{{ applicant.status }}</td>
                      <td class="text-end">
                        <button class="btn btn-sm btn-outline-primary me-1" @click="lookUser({ id: applicant.student_id, name: applicant.student_name, email: applicant.student_email, role: 'student' }, 'student')">Profile</button>
                        <button v-if="applicant.resume_file" class="btn btn-sm btn-outline-secondary" @click="openResumeUrl(applicant.resume_file, applicant.student_id)">Resume</button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <div v-else class="text-muted">No students have applied to this drive yet.</div>
            </div>

            <div class="mt-3 d-flex gap-2">
              <button class="btn btn-primary" @click="submitDriveStatus">Submit</button>
              <button class="btn btn-outline-secondary" @click="selectedDrive = null">Close</button>
            </div>
          </div>
        </div>
      </div>

      <div class="col-md-6">
        <div class="card mb-4">
          <div class="card-header">Student Applications</div>
          <div class="card-body">
            <div class="mb-3 d-flex justify-content-between align-items-center">
              <span class="text-muted">Total applications: {{ applications.length }}</span>
              <button class="btn btn-sm btn-outline-primary" @click="loadApplications">Refresh</button>
            </div>
            <div class="input-group mb-3">
              <input v-model="applicationQuery" class="form-control" placeholder="Search all application fields" />
            </div>
            <div class="list-group application-list">
              <div v-for="app in filteredApplications" :key="app.id" class="list-group-item">
                <div class="d-flex justify-content-between align-items-start gap-2">
                  <div>
                    <strong>#{{ app.id }}</strong> Student ID: {{ app.student_id }}<br />
                    Drive: {{ app.drive_title || app.drive_id }}<br />
                    Company: {{ app.company_name || '—' }}
                  </div>
                  <div class="text-end">
                    <span class="badge bg-secondary mb-2 d-block">{{ app.status }}</span>
                    <button class="btn btn-sm btn-outline-primary" @click="openApplicationDetails(app)">View Detail</button>
                  </div>
                </div>
              </div>
              <div v-if="filteredApplications.length === 0" class="list-group-item text-center text-muted">
                No applications found.
              </div>
            </div>
          </div>
        </div>

        <div class="card mb-4">
          <div class="card-header">Search Companies</div>
          <div class="card-body">
            <div class="input-group mb-3">
              <input v-model="companyQuery" @keyup.enter="searchCompanies" class="form-control" placeholder="Search all company fields" />
              <button class="btn btn-primary" @click="searchCompanies">Search</button>
            </div>
            <div class="table-responsive">
              <table class="table table-sm mb-0">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Status</th>
                    <th class="text-end">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="company in filteredCompanies" :key="company.company_id">
                    <td>{{ company.name }}</td>
                    <td>{{ company.email }}</td>
                    <td>
                      <span v-if="company.blacklisted" class="badge bg-danger">Blacklisted</span>
                      <span v-else-if="!company.is_active" class="badge bg-warning">Inactive</span>
                      <span v-else-if="company.approved" class="badge bg-success">Active</span>
                      <span v-else class="badge bg-secondary">Pending</span>
                    </td>
                    <td class="text-end">
                      <button class="btn btn-sm btn-outline-primary me-1" @click="lookUser(company, 'company')">Look</button>
                      <button class="btn btn-sm btn-danger me-1" @click="blacklistUser(company.user_id)">Blacklist</button>
                      <button class="btn btn-sm btn-secondary me-1" @click="deactivateUser(company.user_id)">Deactivate</button>
                      <button class="btn btn-sm btn-success" @click="activateUser(company.user_id)" :disabled="company.is_active && !company.blacklisted">Activate</button>
                    </td>
                  </tr>
                  <tr v-if="filteredCompanies.length === 0">
                    <td colspan="4" class="text-center py-3">No companies found.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div class="card mb-4">
          <div class="card-header">Search Students</div>
          <div class="card-body">
            <div class="input-group mb-3">
              <input v-model="studentQuery" @keyup.enter="searchStudents" class="form-control" placeholder="Search all student fields" />
              <button class="btn btn-primary" @click="searchStudents">Search</button>
            </div>
            <div class="table-responsive">
              <table class="table table-sm mb-0">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Status</th>
                    <th class="text-end">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="student in filteredStudents" :key="student.student_id">
                    <td>{{ student.name }}</td>
                    <td>{{ student.email }}</td>
                    <td>
                      <span v-if="student.blacklisted" class="badge bg-danger">Blacklisted</span>
                      <span v-else-if="!student.is_active" class="badge bg-warning">Inactive</span>
                      <span v-else class="badge bg-success">Active</span>
                    </td>
                    <td class="text-end">
                      <button class="btn btn-sm btn-outline-primary me-1" @click="lookUser(student, 'student')">Look</button>
                      <button class="btn btn-sm btn-danger me-1" @click="blacklistUser(student.student_id)">Blacklist</button>
                      <button class="btn btn-sm btn-secondary me-1" @click="deactivateUser(student.student_id)">Deactivate</button>
                      <button class="btn btn-sm btn-success" @click="activateUser(student.student_id)" :disabled="student.is_active && !student.blacklisted">Activate</button>
                    </td>
                  </tr>
                  <tr v-if="filteredStudents.length === 0">
                    <td colspan="4" class="text-center py-3">No students found.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div class="card mb-4">
          <div class="card-header">Activity History</div>
          <div class="card-body">
            <div class="list-group history-list">
              <div v-for="entry in historyEntries" :key="entry.id" class="list-group-item">
                <div class="d-flex justify-content-between align-items-start gap-2">
                  <div>
                    <strong>{{ entry.action }}</strong><br />
                    <small class="text-muted">{{ entry.user_name || entry.user_email || 'System' }} • {{ formatDate(entry.created_at) }}</small>
                  </div>
                  <span class="badge bg-secondary">{{ entry.entity_type }}</span>
                </div>
                <div v-if="entry.details" class="small mt-2 text-muted">{{ entry.details }}</div>
              </div>
              <div v-if="historyEntries.length === 0" class="list-group-item text-center text-muted">No history yet.</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="mb-4">
      <NotificationCenter />
    </div>

    <div v-if="selectedUser" class="modal d-block bg-dark bg-opacity-50" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">User Details</h5>
            <button class="btn-close" @click="selectedUser = null"></button>
          </div>
          <div class="modal-body">
            <div v-if="selectedUser.loading" class="text-muted">Loading details...</div>
            <div v-else>
              <p><strong>Name:</strong> {{ selectedUser.name }}</p>
              <p><strong>Email:</strong> {{ selectedUser.email }}</p>
              <p><strong>Role:</strong> {{ selectedUser.role }}</p>
              <p><strong>Status:</strong> {{ selectedUser.blacklisted ? 'Blocklisted' : (selectedUser.is_active ? 'Active' : 'Inactive') }}</p>
              <div v-if="selectedUser.profile && Object.keys(selectedUser.profile).length" class="mt-3">
                <h6>Profile</h6>
                <pre class="small mb-0">{{ JSON.stringify(selectedUser.profile, null, 2) }}</pre>
              </div>
              <div v-if="selectedUser.company" class="mt-3">
                <h6>Company Details</h6>
                <p class="mb-1"><strong>Company:</strong> {{ selectedUser.company.name }}</p>
                <p class="mb-1"><strong>Approved:</strong> {{ selectedUser.company.approved ? 'Yes' : 'No' }}</p>
                <p class="mb-0"><strong>Website:</strong> {{ selectedUser.company.website || '—' }}</p>
              </div>
              <div v-if="selectedUser.resume_file" class="mt-3">
                <button class="btn btn-outline-secondary btn-sm" @click="openUserResume(selectedUser.id)">View Resume</button>
              </div>
            </div>
          </div>
          <div class="modal-footer justify-content-between">
            <div>
              <button class="btn btn-outline-danger btn-sm" @click="blacklistUser(selectedUser.id)">Blocklist</button>
              <button class="btn btn-outline-success btn-sm ms-2" @click="approveUser(selectedUser.id)">Approve</button>
              <button class="btn btn-outline-warning btn-sm ms-2" @click="rejectUser(selectedUser.id)">Reject</button>
            </div>
            <button class="btn btn-secondary" @click="selectedUser = null">Close</button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="selectedApplication" class="modal d-block bg-dark bg-opacity-50" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Application Details</h5>
            <button class="btn-close" @click="selectedApplication = null"></button>
          </div>
          <div class="modal-body">
            <p><strong>Student:</strong> {{ selectedApplication.student_name || '—' }}</p>
            <p><strong>Email:</strong> {{ selectedApplication.student_email || '—' }}</p>
            <p><strong>Drive:</strong> {{ selectedApplication.drive_title || '—' }}</p>
            <p><strong>Company:</strong> {{ selectedApplication.company_name || '—' }}</p>
            <p><strong>Status:</strong> {{ selectedApplication.status }}</p>
            <p><strong>Applied On:</strong> {{ formatDate(selectedApplication.applied_on) }}</p>
          </div>
          <div class="modal-footer">
            <button class="btn btn-outline-primary btn-sm" @click="showApplicationStudentProfile(selectedApplication)">View Student Profile</button>
            <button class="btn btn-outline-secondary btn-sm" @click="openApplicationResume(selectedApplication)">View Resume</button>
            <button class="btn btn-secondary" @click="selectedApplication = null">Close</button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="message" class="alert alert-info mt-3">{{ message }}</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import api, { setAuthToken } from '../services/api'
import Chart from 'chart.js/auto'
import NotificationCenter from './NotificationCenter.vue'

const summary = ref({
  total_students: 0,
  total_companies: 0,
  total_drives: 0,
  pending_companies: 0,
  pending_drives: 0,
})
const pendingCompanies = ref([])
const allDrives = ref([])
const applications = ref([])
const companies = ref([])
const students = ref([])
const historyEntries = ref([])
const companyQuery = ref('')
const studentQuery = ref('')
const pendingCompanyQuery = ref('')
const applicationQuery = ref('')
const message = ref('')
const operationsMessage = ref('')
const driveModes = ['All', 'Pending', 'Approved', 'Rejected']
const activeDriveMode = ref('All')
const selectedDrive = ref(null)
const selectedDriveStatus = ref('Pending')
const selectedUser = ref(null)
const selectedApplication = ref(null)
const driveReviewApplicants = ref([])
const chartCanvas = ref(null)
const companyChartCanvas = ref(null)
const chartInstance = ref(null)
const companyChartInstance = ref(null)

const cards = computed(() => [
  { label: 'Students', value: summary.value.total_students },
  { label: 'Companies', value: summary.value.total_companies },
  { label: 'Drives', value: summary.value.total_drives },
  { label: 'Pending Companies', value: summary.value.pending_companies },
  { label: 'Pending Drives', value: summary.value.pending_drives },
])

const chartCounts = computed(() => {
  const pending = allDrives.value.filter((drive) => drive.status === 'Pending').length
  const approved = allDrives.value.filter((drive) => drive.status === 'Approved').length
  const rejected = allDrives.value.filter((drive) => drive.status === 'Rejected').length
  return { pending, approved, rejected }
})

const companyChartCounts = computed(() => {
  const pending = companies.value.filter((company) => company.approved === false && company.is_active !== false && !company.blacklisted).length
  const approved = companies.value.filter((company) => company.approved === true).length
  const rejected = companies.value.filter((company) => company.approved === false && company.is_active === false).length
  return { pending, approved, rejected }
})

const filteredDrives = computed(() => {
  if (activeDriveMode.value === 'All') {
    return allDrives.value
  }
  return allDrives.value.filter((drive) => drive.status === activeDriveMode.value)
})

const filteredPendingCompanies = computed(() => {
  const q = pendingCompanyQuery.value.trim().toLowerCase()
  if (!q) return pendingCompanies.value
  return pendingCompanies.value.filter((company) => [company.name, company.email, company.approved ? 'approved' : 'pending'].join(' ').toLowerCase().includes(q))
})

const filteredApplications = computed(() => {
  const q = applicationQuery.value.trim().toLowerCase()
  if (!q) return applications.value
  return applications.value.filter((app) => [app.id, app.student_id, app.drive_id, app.status, app.drive_title, app.company_name].join(' ').toLowerCase().includes(q))
})

const filteredCompanies = computed(() => {
  const q = companyQuery.value.trim().toLowerCase()
  if (!q) return companies.value
  return companies.value.filter((company) => [company.name, company.email, company.website, company.hr_contact, company.status].join(' ').toLowerCase().includes(q))
})

const filteredStudents = computed(() => {
  const q = studentQuery.value.trim().toLowerCase()
  if (!q) return students.value
  return students.value.filter((student) => [student.name, student.email].join(' ').toLowerCase().includes(q))
})

function notify(text) {
  message.value = text
  window.setTimeout(() => {
    if (message.value === text) {
      message.value = ''
    }
  }, 3000)
}

function formatDate(value) {
  if (!value) return '—'
  const dateValue = new Date(value)
  if (Number.isNaN(dateValue.getTime())) return value
  return dateValue.toLocaleDateString()
}

function openDriveDetails(drive) {
  selectedDrive.value = { ...drive }
  selectedDriveStatus.value = drive.status || 'Pending'
  loadDriveReview(drive.drive_id)
}

async function loadDriveReview(driveId) {
  try {
    const res = await api.get(`/admin/drives/${driveId}/details`)
    const detailPayload = res.data || {}
    driveReviewApplicants.value = detailPayload.applicants || []
    if (selectedDrive.value) {
      selectedDrive.value = {
        ...selectedDrive.value,
        ...detailPayload.drive,
        company: detailPayload.company || null,
        company_name: detailPayload.company?.name || selectedDrive.value.company_name || 'Unknown',
      }
    }
  } catch (e) {
    driveReviewApplicants.value = []
  }
}

function openApplicationDetails(app) {
  selectedApplication.value = app
}

function showApplicationStudentProfile(app) {
  if (!app?.student_id) return
  lookUser({ id: app.student_id, name: app.student_name, email: app.student_email, role: 'student' }, 'student')
}

function openApplicationResume(app) {
  if (!app?.student_id) return
  window.open(`/api/admin/users/${app.student_id}/resume`, '_blank')
}

function openResumeUrl(filename, userId) {
  if (!filename) {
    window.open(`/api/admin/users/${userId}/resume`, '_blank')
    return
  }
  window.open(`/api/admin/users/${userId}/resume`, '_blank')
}

async function lookUser(user, type) {
  const userId = user.user_id || user.student_id || user.id
  if (!userId) return
  selectedUser.value = { id: userId, name: user.name, email: user.email, role: type, loading: true }
  try {
    const res = await api.get(`/admin/users/${userId}/details`)
    selectedUser.value = { ...selectedUser.value, ...res.data, loading: false }
  } catch (e) {
    selectedUser.value = { ...selectedUser.value, loading: false, error: e.response?.data?.message || 'Could not load details' }
  }
}

function openUserResume(userId) {
  if (!userId) return
  window.open(`/api/admin/users/${userId}/resume`, '_blank')
}

async function loadSummary() {
  try {
    const res = await api.get('/admin/summary')
    summary.value = res.data
  } catch (e) {
    notify(e.response?.data?.message || 'Failed to load summary')
  }
}

async function loadPendingCompanies() {
  try {
    const res = await api.get('/admin/companies')
    pendingCompanies.value = res.data.filter((c) => !c.approved)
  } catch (e) {
    pendingCompanies.value = []
  }
}

async function loadDrives() {
  try {
    const res = await api.get('/admin/drives')
    allDrives.value = res.data
  } catch (e) {
    allDrives.value = []
  }
}

async function loadApplications() {
  try {
    const res = await api.get('/applications')
    applications.value = res.data
  } catch (e) {
    applications.value = []
  }
}

async function loadHistory() {
  try {
    const res = await api.get('/admin/history')
    historyEntries.value = res.data
  } catch (e) {
    historyEntries.value = []
  }
}

async function loadCompanies(q = '') {
  try {
    const res = await api.get('/admin/companies', { params: { q } })
    companies.value = res.data
  } catch (e) {
    companies.value = []
  }
}

async function loadStudents(q = '') {
  try {
    const res = await api.get('/admin/students', { params: { q } })
    students.value = res.data
  } catch (e) {
    students.value = []
  }
}

async function approveCompany(id) {
  try {
    await api.post(`/admin/approve_company/${id}`)
    notify('Company approved')
    await refreshAll()
  } catch (e) {
    notify(e.response?.data?.message || 'Could not approve company')
  }
}

async function rejectCompany(id) {
  try {
    await api.post(`/admin/reject_company/${id}`)
    notify('Company rejected')
    await refreshAll()
  } catch (e) {
    notify(e.response?.data?.message || 'Could not reject company')
  }
}

async function submitDriveStatus() {
  if (!selectedDrive.value) return
  try {
    await api.post(`/admin/drives/${selectedDrive.value.drive_id}/status`, { status: selectedDriveStatus.value })
    notify(`Drive marked as ${selectedDriveStatus.value}`)
    selectedDrive.value = null
    await refreshAll()
  } catch (e) {
    notify(e.response?.data?.message || 'Could not update drive status')
  }
}

async function blacklistUser(userId) {
  try {
    await api.post(`/admin/users/${userId}/blacklist`)
    notify('User blacklisted')
    await refreshAll()
  } catch (e) {
    notify(e.response?.data?.message || 'Could not blacklist user')
  }
}

async function deactivateUser(userId) {
  try {
    await api.post(`/admin/users/${userId}/deactivate`)
    notify('User deactivated')
    await refreshAll()
  } catch (e) {
    notify(e.response?.data?.message || 'Could not deactivate user')
  }
}

async function activateUser(userId) {
  try {
    await api.post(`/admin/users/${userId}/activate`)
    notify('User activated')
    await refreshAll()
  } catch (e) {
    notify(e.response?.data?.message || 'Could not activate user')
  }
}

async function searchCompanies() {
  await loadCompanies(companyQuery.value)
}

async function searchStudents() {
  await loadStudents(studentQuery.value)
}

async function approveUser(userId) {
  try {
    await api.post(`/admin/users/${userId}/approve`)
    notify('User approved')
    selectedUser.value = null
    await refreshAll()
  } catch (e) {
    notify(e.response?.data?.message || 'Could not approve user')
  }
}

async function rejectUser(userId) {
  try {
    await api.post(`/admin/users/${userId}/reject`)
    notify('User rejected')
    selectedUser.value = null
    await refreshAll()
  } catch (e) {
    notify(e.response?.data?.message || 'Could not reject user')
  }
}

async function generateReport() {
  try {
    const res = await api.get('/admin/report/monthly')
    operationsMessage.value = `Report generated at ${res.data.path}`
  } catch (e) {
    operationsMessage.value = e.response?.data?.message || 'Could not generate report'
  }
}

async function triggerReminders() {
  try {
    const res = await api.post('/admin/notifications/reminders')
    operationsMessage.value = `Reminders prepared for ${res.data.message_count} students`
  } catch (e) {
    operationsMessage.value = e.response?.data?.message || 'Could not trigger reminders'
  }
}

async function refreshAll() {
  await Promise.all([loadSummary(), loadPendingCompanies(), loadDrives(), loadApplications(), loadHistory(), loadCompanies(companyQuery.value), loadStudents(studentQuery.value)])
}

function renderChart() {
  if (!chartCanvas.value) return
  if (chartInstance.value) {
    chartInstance.value.destroy()
  }
  chartInstance.value = new Chart(chartCanvas.value, {
    type: 'pie',
    data: {
      labels: ['Pending', 'Approved', 'Rejected'],
      datasets: [{
        data: [chartCounts.value.pending, chartCounts.value.approved, chartCounts.value.rejected],
        backgroundColor: ['#f4b400', '#198754', '#dc3545'],
      }],
    },
    options: { responsive: true, plugins: { legend: { position: 'bottom' } } },
  })
}

function renderCompanyChart() {
  if (!companyChartCanvas.value) return
  if (companyChartInstance.value) {
    companyChartInstance.value.destroy()
  }
  companyChartInstance.value = new Chart(companyChartCanvas.value, {
    type: 'pie',
    data: {
      labels: ['Pending', 'Approved', 'Rejected'],
      datasets: [{
        data: [companyChartCounts.value.pending, companyChartCounts.value.approved, companyChartCounts.value.rejected],
        backgroundColor: ['#f4b400', '#198754', '#dc3545'],
      }],
    },
    options: { responsive: true, plugins: { legend: { position: 'bottom' } } },
  })
}

watch(chartCounts, () => {
  nextTick(() => renderChart())
}, { deep: true })

watch(companyChartCounts, () => {
  nextTick(() => renderCompanyChart())
}, { deep: true })

onMounted(() => {
  setAuthToken(localStorage.getItem('ppa_token'))
  refreshAll().then(() => {
    renderChart()
    renderCompanyChart()
  })
})
</script>

<style scoped>
.admin-dashboard .card {
  min-height: 120px;
}
.admin-dashboard .application-list .list-group-item {
  word-break: break-word;
}
</style>

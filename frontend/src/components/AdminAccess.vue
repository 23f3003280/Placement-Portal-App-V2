<template>
  <div>
    <h2>User Access Management</h2>

    <!-- Create User Form -->
    <div class="create-user-form">
      <h3>Create New User</h3>
      <form @submit.prevent="createUser">
        <input v-model="newUser.username" placeholder="Username" required />
        <input v-model="newUser.email" type="email" placeholder="Email" required />
        <input v-model="newUser.password" type="password" placeholder="Password" required />
        <input v-model="newUser.role" placeholder="Role (e.g., user)" required />
        <button type="submit">Create User</button>
      </form>
    </div>

    <p v-if="loading">Loading users...</p>
    <p v-if="error" style="color: red;">{{ error }}</p>
    <p v-if="success" style="color: green;">{{ success }}</p>

    <!-- Users Table -->
    <table v-if="users.length > 0">
      <thead>
        <tr>
          <th>ID</th>
          <th>Username</th>
          <th>Email</th>
          <th>Role</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in users" :key="user.id">
          <td>{{ user.id }}</td>
          <td>
            <input v-if="user.editing" v-model="user.editable.username" />
            <span v-else>{{ user.username }}</span>
          </td>
          <td>
            <input v-if="user.editing" v-model="user.editable.email" />
            <span v-else>{{ user.email }}</span>
          </td>
          <td>
            <input v-if="user.editing" v-model="user.editable.role" />
            <span v-else>{{ user.role }}</span>
          </td>
          <td>
            <div v-if="user.editing">
              <button @click="saveUser(user)">Save</button>
              <button @click="cancelEdit(user)">Cancel</button>
            </div>
            <div v-else>
              <button @click="toggleEdit(user)">Edit</button>
              <button @click="deleteUser(user.id)">Delete</button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'AdminAccess',
  props: ['initialUsers'],
  data() {
    return {
      users: [],
      loading: false,
      error: null,
      success: null,
      newUser: {
        username: '',
        email: '',
        password: '',
        role: 'user',
      },
    };
  },
  watch: {
    initialUsers: {
      immediate: true,
      handler(newVal) {
        this.users = newVal.map(user => ({ ...user, editing: false, editable: { ...user } }));
      }
    }
  },
  methods: {
    toggleEdit(user) {
      user.editing = !user.editing;
      if (user.editing) {
        user.editable = { ...user };
      }
    },
    cancelEdit(user) {
      user.editing = false;
    },
    async saveUser(user) {
      this.error = null;
      this.success = null;
      try {
        const token = localStorage.getItem('token');
        await axios.put(`http://localhost:5000/api/users/${user.id}`, user.editable, {
          headers: { Authorization: `Bearer ${token}` },
        });
        user.editing = false;
        this.success = `User ${user.id} updated successfully.`;
        this.$emit('users-updated'); // Refresh data
      } catch (err) {
        this.error = `Failed to update user ${user.id}.`;
        console.error(err);
      }
    },
    async deleteUser(userId) {
      this.error = null;
      this.success = null;
      if (!confirm('Are you sure you want to delete this user?')) {
        return;
      }
      try {
        const token = localStorage.getItem('token');
        await axios.delete(`http://localhost:5000/api/users/${userId}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        this.success = `User ${userId} deleted successfully.`;
        this.$emit('users-updated'); // Refresh data
      } catch (err) {
        this.error = `Failed to delete user ${userId}.`;
        console.error(err);
      }
    },
    async createUser() {
      this.error = null;
      this.success = null;
      try {
        const token = localStorage.getItem('token');
        await axios.post('http://localhost:5000/api/users', this.newUser, {
          headers: { Authorization: `Bearer ${token}` },
        });
        this.success = `User '${this.newUser.username}' created successfully.`;
        // Reset form
        this.newUser = {
          username: '',
          email: '',
          password: '',
          role: 'user',
        };
        this.$emit('users-updated'); // Refresh data
      } catch (err) {
        this.error = err.response?.data?.message || 'Failed to create user.';
        console.error(err);
      }
    },
  },
};
</script>

<style scoped>
table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}
th, td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
}
th {
  background-color: #f2f2f2;
}
button {
  margin-right: 5px;
}
.create-user-form {
  margin-bottom: 30px;
  padding: 15px;
  border: 1px solid #ccc;
  border-radius: 5px;
}
.create-user-form h3 {
  margin-top: 0;
}
.create-user-form input {
  margin-right: 10px;
}
</style>
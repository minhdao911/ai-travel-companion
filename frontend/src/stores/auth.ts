import { defineStore } from "pinia";
import { checkAdmin, verifyAdmin } from "@/services/api";

const useAuthStore = defineStore("auth_store", {
  state: () => ({
    isAdmin: false,
    adminChecked: false,
  }),
  actions: {
    async verifyAdmin(username: string, password: string) {
      try {
        this.isAdmin = await verifyAdmin(username, password);
        return this.isAdmin;
      } catch (error) {
        console.error(error);
        return false;
      }
    },
    async checkAdmin() {
      try {
        if (this.adminChecked) return;

        this.isAdmin = await checkAdmin();
        return this.isAdmin;
      } catch (error) {
        console.error(error);
        return false;
      } finally {
        this.adminChecked = true;
      }
    },
  },
});

export default useAuthStore;

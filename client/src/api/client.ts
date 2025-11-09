import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig, AxiosRequestConfig } from "axios";
import { API_BASE_URL, STORAGE_KEYS } from "@/config";

export class ApiClient {
  private instance: AxiosInstance;

  constructor() {
    this.instance = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        "Content-Type": "application/json",
      },
      timeout: 10000000000000000000000000000, //changed to 10000 seconds
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor - automatically inject auth token
    this.instance.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        // Check if we're in the browser
        if (typeof window !== "undefined") {
          const token = localStorage.getItem(STORAGE_KEYS.AUTH_TOKEN);
          
          if (token && config.headers) {
            config.headers.Authorization = `Bearer ${token}`;
          }
        }
        
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor - handle errors globally
    this.instance.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response) {
          // Server responded with error
          const errorMessage = (error.response.data as any)?.detail || "Request failed";
          throw new Error(errorMessage);
        } else if (error.request) {
          // Request made but no response
          throw new Error("No response from server");
        } else {
          // Something else happened
          throw new Error(error.message || "Request failed");
        }
      }
    );
  }

  async get<T>(endpoint: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.instance.get<T>(endpoint, config);
    return response.data;
  }

  async post<T>(endpoint: string, body?: unknown): Promise<T> {
    const response = await this.instance.post<T>(endpoint, body);
    return response.data;
  }

  async put<T>(endpoint: string, body?: unknown): Promise<T> {
    const response = await this.instance.put<T>(endpoint, body);
    return response.data;
  }

  async delete<T>(endpoint: string): Promise<T> {
    const response = await this.instance.delete<T>(endpoint);
    return response.data;
  }

  async patch<T>(endpoint: string, body?: unknown): Promise<T> {
    const response = await this.instance.patch<T>(endpoint, body);
    return response.data;
  }
}

export const apiClient = new ApiClient();

# AI Security Lab v5.0 - Quick Start Guide

## 🎯 Goal: Build Mobile App MVP in 3 Months

This guide helps you start v5.0 development **immediately** with the highest-priority features.

---

## 📱 Priority 1: Mobile App (Weeks 1-10)

### Step 1: Initialize React Native Project (Day 1)

```bash
# Install React Native CLI
npm install -g expo-cli

# Create new project
cd /home/user/ai-security-lab-v4
npx create-expo-app mobile-app --template blank-typescript

cd mobile-app

# Install core dependencies
npm install @react-navigation/native @react-navigation/stack
npm install react-native-screens react-native-safe-area-context
npm install @tanstack/react-query axios
npm install zustand
npm install socket.io-client
npm install expo-secure-store
npm install expo-notifications

# Install dev dependencies
npm install --save-dev @types/react @types/react-native
```

### Step 2: Project Structure

```
mobile-app/
├── src/
│   ├── api/              # API client (axios + react-query)
│   │   ├── client.ts
│   │   ├── auth.ts
│   │   ├── cameras.ts
│   │   └── alerts.ts
│   ├── components/       # Reusable components
│   │   ├── AlertCard.tsx
│   │   ├── CameraCard.tsx
│   │   └── Button.tsx
│   ├── screens/          # App screens
│   │   ├── Auth/
│   │   │   └── LoginScreen.tsx
│   │   ├── Dashboard/
│   │   │   └── DashboardScreen.tsx
│   │   ├── Cameras/
│   │   │   ├── CameraListScreen.tsx
│   │   │   └── LiveViewScreen.tsx
│   │   └── Alerts/
│   │       ├── AlertListScreen.tsx
│   │       └── AlertDetailScreen.tsx
│   ├── navigation/       # Navigation setup
│   │   └── AppNavigator.tsx
│   ├── store/           # State management (zustand)
│   │   ├── authStore.ts
│   │   └── alertStore.ts
│   ├── hooks/           # Custom hooks
│   │   ├── useAuth.ts
│   │   └── useNotifications.ts
│   ├── types/           # TypeScript types
│   │   └── index.ts
│   └── utils/           # Utilities
│       └── constants.ts
├── app.json
├── package.json
└── tsconfig.json
```

### Step 3: Authentication Implementation

**src/api/client.ts**:
```typescript
import axios from 'axios';
import * as SecureStore from 'expo-secure-store';

const API_URL = 'http://your-api-url:8000';

export const apiClient = axios.create({
  baseURL: API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add JWT token
apiClient.interceptors.request.use(async (config) => {
  const token = await SecureStore.getItemAsync('jwt_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

**src/api/auth.ts**:
```typescript
import { apiClient } from './client';

export const authAPI = {
  login: async (username: string, password: string) => {
    const response = await apiClient.post('/api/auth/login', {
      username,
      password,
    });
    return response.data;
  },

  logout: async () => {
    const response = await apiClient.post('/api/auth/logout');
    return response.data;
  },

  refreshToken: async (refreshToken: string) => {
    const response = await apiClient.post('/api/auth/refresh', {
      refresh_token: refreshToken,
    });
    return response.data;
  },
};
```

**src/store/authStore.ts**:
```typescript
import { create } from 'zustand';
import * as SecureStore from 'expo-secure-store';

interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  loadToken: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  isAuthenticated: false,
  user: null,
  token: null,

  login: async (username, password) => {
    const response = await authAPI.login(username, password);
    await SecureStore.setItemAsync('jwt_token', response.access_token);
    await SecureStore.setItemAsync('refresh_token', response.refresh_token);
    set({
      isAuthenticated: true,
      user: response.user,
      token: response.access_token,
    });
  },

  logout: async () => {
    await authAPI.logout();
    await SecureStore.deleteItemAsync('jwt_token');
    await SecureStore.deleteItemAsync('refresh_token');
    set({ isAuthenticated: false, user: null, token: null });
  },

  loadToken: async () => {
    const token = await SecureStore.getItemAsync('jwt_token');
    if (token) {
      set({ isAuthenticated: true, token });
    }
  },
}));
```

**src/screens/Auth/LoginScreen.tsx**:
```typescript
import React, { useState } from 'react';
import { View, TextInput, Button, StyleSheet } from 'react-native';
import { useAuthStore } from '../../store/authStore';

export const LoginScreen = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const login = useAuthStore((state) => state.login);

  const handleLogin = async () => {
    try {
      await login(username, password);
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  return (
    <View style={styles.container}>
      <TextInput
        style={styles.input}
        placeholder="Username"
        value={username}
        onChangeText={setUsername}
        autoCapitalize="none"
      />
      <TextInput
        style={styles.input}
        placeholder="Password"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
      />
      <Button title="Login" onPress={handleLogin} />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    padding: 20,
  },
  input: {
    height: 50,
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 8,
    paddingHorizontal: 15,
    marginBottom: 15,
  },
});
```

### Step 4: Camera List Implementation

**src/api/cameras.ts**:
```typescript
import { apiClient } from './client';

export const camerasAPI = {
  getCameras: async () => {
    const response = await apiClient.get('/api/dashboard/cameras');
    return response.data;
  },

  getCameraById: async (cameraId: string) => {
    const response = await apiClient.get(`/api/cameras/${cameraId}`);
    return response.data;
  },
};
```

**src/screens/Cameras/CameraListScreen.tsx**:
```typescript
import React from 'react';
import { View, FlatList, StyleSheet } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { camerasAPI } from '../../api/cameras';
import { CameraCard } from '../../components/CameraCard';

export const CameraListScreen = ({ navigation }) => {
  const { data, isLoading } = useQuery({
    queryKey: ['cameras'],
    queryFn: camerasAPI.getCameras,
  });

  return (
    <View style={styles.container}>
      <FlatList
        data={data?.cameras || []}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <CameraCard
            camera={item}
            onPress={() =>
              navigation.navigate('LiveView', { cameraId: item.id })
            }
          />
        )}
      />
    </View>
  );
};
```

### Step 5: Push Notifications Setup

**src/hooks/useNotifications.ts**:
```typescript
import { useEffect, useRef } from 'react';
import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';

Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

export const useNotifications = () => {
  const notificationListener = useRef<any>();
  const responseListener = useRef<any>();

  useEffect(() => {
    registerForPushNotifications();

    notificationListener.current =
      Notifications.addNotificationReceivedListener((notification) => {
        console.log('Notification received:', notification);
      });

    responseListener.current =
      Notifications.addNotificationResponseReceivedListener((response) => {
        console.log('Notification response:', response);
        // Navigate to alert detail screen
      });

    return () => {
      Notifications.removeNotificationSubscription(
        notificationListener.current
      );
      Notifications.removeNotificationSubscription(responseListener.current);
    };
  }, []);

  const registerForPushNotifications = async () => {
    if (!Device.isDevice) {
      console.log('Push notifications only work on physical devices');
      return;
    }

    const { status: existingStatus } =
      await Notifications.getPermissionsAsync();
    let finalStatus = existingStatus;

    if (existingStatus !== 'granted') {
      const { status } = await Notifications.requestPermissionsAsync();
      finalStatus = status;
    }

    if (finalStatus !== 'granted') {
      console.log('Failed to get push token for push notification!');
      return;
    }

    const token = (await Notifications.getExpoPushTokenAsync()).data;
    console.log('Push token:', token);

    // Send token to backend
    await apiClient.post('/api/devices/register', {
      push_token: token,
      platform: Device.osName,
    });
  };
};
```

---

## 🔔 Priority 2: Push Notification Backend (Week 3-4)

### Step 1: Create Notification Service

**services/notifications/main.py**:
```python
"""
Push Notification Service
Handles FCM and APNs push notifications
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import firebase_admin
from firebase_admin import credentials, messaging
import logging

app = FastAPI(title="Push Notification Service")
logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
cred = credentials.Certificate("firebase-credentials.json")
firebase_admin.initialize_app(cred)


class PushNotification(BaseModel):
    """Push notification model."""
    user_ids: List[str]
    title: str
    body: str
    data: Optional[dict] = None
    priority: str = "high"


class NotificationService:
    """Push notification service."""

    async def send_to_users(
        self,
        user_ids: List[str],
        notification: PushNotification
    ):
        """Send push notification to multiple users."""

        # Get device tokens from database
        tokens = await self._get_device_tokens(user_ids)

        if not tokens:
            logger.warning(f"No device tokens found for users: {user_ids}")
            return

        # Create FCM message
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=notification.title,
                body=notification.body,
            ),
            data=notification.data or {},
            tokens=tokens,
            android=messaging.AndroidConfig(
                priority=notification.priority,
            ),
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        sound="default",
                        badge=1,
                    ),
                ),
            ),
        )

        # Send notification
        response = messaging.send_multicast(message)
        logger.info(
            f"Sent {response.success_count} notifications successfully"
        )

        if response.failure_count > 0:
            logger.error(
                f"Failed to send {response.failure_count} notifications"
            )

        return {
            "success_count": response.success_count,
            "failure_count": response.failure_count,
        }


notification_service = NotificationService()


@app.post("/send")
async def send_notification(notification: PushNotification):
    """Send push notification endpoint."""
    try:
        result = await notification_service.send_to_users(
            notification.user_ids,
            notification
        )
        return result
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/threat-alert")
async def send_threat_alert(
    threat_id: str,
    threat_level: str,
    camera_id: str,
    threat_score: float
):
    """Send threat alert notification."""

    # Get users who should receive this alert
    users = await _get_alert_recipients(threat_level)

    notification = PushNotification(
        user_ids=users,
        title=f"{threat_level.upper()} Threat Detected",
        body=f"Camera {camera_id} detected a threat (score: {threat_score:.2f})",
        data={
            "type": "threat_alert",
            "threat_id": threat_id,
            "threat_level": threat_level,
            "camera_id": camera_id,
            "threat_score": str(threat_score),
        },
        priority="high" if threat_level in ["critical", "high"] else "normal",
    )

    return await notification_service.send_to_users(users, notification)
```

### Step 2: Integrate with Threat Detector

**services/intelligence/threat-detector/main.py** (add to existing):
```python
import httpx

# Add to threat detection pipeline
async def _trigger_threat_alert(self, analysis: ThreatAnalysis):
    """Trigger alert for high-priority threats."""
    try:
        await self.alert_manager.create_alert(...)

        # Send push notification
        if analysis.requires_response:
            async with httpx.AsyncClient() as client:
                await client.post(
                    "http://notification-service:8002/threat-alert",
                    json={
                        "threat_id": analysis.detection_id,
                        "threat_level": analysis.threat_level.value,
                        "camera_id": analysis.camera_id,
                        "threat_score": analysis.threat_score,
                    }
                )
    except Exception as e:
        logger.error(f"Failed to trigger threat alert: {e}")
```

---

## 🚀 Quick Win: Deploy Notification Service

### Docker Compose Addition

**docker/compose/docker-compose.yml** (add):
```yaml
  notification-service:
    <<: *common
    build: ./services/notifications
    container_name: notification-service
    environment:
      FIREBASE_CREDENTIALS: /app/firebase-credentials.json
      DATABASE_URL: postgresql://security:${POSTGRES_PASSWORD}@timescaledb:5432/security_events
    volumes:
      - ./firebase-credentials.json:/app/firebase-credentials.json:ro
    ports:
      - "8002:8002"
    depends_on:
      - timescaledb
```

### Deploy

```bash
# Start notification service
docker-compose -f docker/compose/docker-compose.yml up -d notification-service

# Verify
curl http://localhost:8002/health
```

---

## 📝 Week 1 Action Items

**Day 1-2**: Mobile App Setup
- [ ] Initialize React Native project
- [ ] Set up project structure
- [ ] Configure TypeScript

**Day 3-4**: Authentication
- [ ] Implement login screen
- [ ] Add JWT token management
- [ ] Test authentication flow

**Day 5**: Camera List
- [ ] Create camera list screen
- [ ] Implement API integration
- [ ] Add pull-to-refresh

---

## 🎯 Success Criteria (Week 10)

- ✅ Mobile app runs on iOS + Android
- ✅ Users can log in with JWT
- ✅ Users can view camera list
- ✅ Users receive push notifications for threats
- ✅ Users can view and acknowledge alerts
- ✅ App has 0 critical bugs

---

## 📚 Resources

- React Native Docs: https://reactnative.dev
- Expo Docs: https://docs.expo.dev
- React Query: https://tanstack.com/query
- Firebase Cloud Messaging: https://firebase.google.com/docs/cloud-messaging

---

**Ready to start? Run the commands above and begin building! 🚀**

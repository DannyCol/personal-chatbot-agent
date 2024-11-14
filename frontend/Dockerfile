# This frontend container will only be run locally for development

# Use an official Node.js runtime based on Alpine
FROM node:18-alpine

# Set the working directory in the container
WORKDIR /app

# Copy the package.json and package-lock.json files
COPY package*.json ./

# Install dependencies
RUN npm ci --silent

# Copy the rest of the application code
COPY . .

# Expose port 5173 (default Vite development server port)
EXPOSE 5173

# Run the development server
CMD ["npm", "run", "dev"]
# variables
NON_FRONTEND_SERVICES = $(shell docker compose config --services | grep -v '^frontend$$')

# targets
.PHONY: dev test down build

# fastest dockerized option: no-bundle local development w/proxy'ed api calls to backend
dev: down
	docker compose up --build

# serve the bundled frontend via the backend
test: down build
	docker compose up --build $(NON_FRONTEND_SERVICES)

# bundle the frontend, you should do `npm ci` or install node modules otherwise first
build:
	# build bundle and place it in the backend
	cd frontend && npm run build
	rm -rf backend/dist
	mv frontend/dist backend

down:
	docker compose down

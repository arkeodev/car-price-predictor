#!/bin/bash

# Set script to exit on any error
set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Error handling function
handle_error() {
    log "${RED}❌ Error on line $1${NC}"
    exit 1
}

# Set up error handling
trap 'handle_error $LINENO' ERR

# Check if API is running
log "${YELLOW}🔍 Checking if API is available...${NC}"
if ! curl -s "http://localhost:8000/health" > /dev/null; then
    log "${RED}❌ API is not running at http://localhost:8000${NC}"
    exit 1
fi
log "${GREEN}✅ API is running${NC}"

# Function to add a car and handle response
add_car() {
    local model=$1
    local data=$2
    
    log "${YELLOW}📤 Adding $model...${NC}"
    response=$(curl -s -w "\n%{http_code}" -X POST "http://localhost:8000/cars" \
        -H "Content-Type: application/json" \
        -d "$data")
    
    # Get status code from last line
    status_code=$(echo "$response" | tail -n1)
    # Get response body without status code
    body=$(echo "$response" | sed \$d)
    
    if [ "$status_code" -eq 200 ]; then
        log "${GREEN}✅ Successfully added $model${NC}"
    else
        log "${RED}❌ Failed to add $model. Status: $status_code${NC}"
        log "${RED}Response: $body${NC}"
        return 1
    fi
}

# Initialize counters
total_cars=0
successful_adds=0

log "${YELLOW}🚀 Starting car import process...${NC}"

# Fiesta variants
log "\n${YELLOW}📦 Adding Fiesta variants...${NC}"
add_car "Fiesta 1.0" '{"model":"Fiesta","year":2020,"price":12500,"transmission":"Manual","mileage":25000,"fueltype":"Petrol","tax":150,"mpg":55.4,"engine_size":1.0}' && ((successful_adds++))
((total_cars++))

add_car "Fiesta 1.1" '{"model":"Fiesta","year":2021,"price":14500,"transmission":"Automatic","mileage":18000,"fueltype":"Petrol","tax":155,"mpg":52.3,"engine_size":1.1}' && ((successful_adds++))
((total_cars++))

add_car "Fiesta ST" '{"model":"Fiesta ST","year":2022,"price":22000,"transmission":"Manual","mileage":8000,"fueltype":"Petrol","tax":165,"mpg":45.6,"engine_size":1.5}' && ((successful_adds++))
((total_cars++))

# Focus variants
log "\n${YELLOW}📦 Adding Focus variants...${NC}"
add_car "Focus 1.5" '{"model":"Focus","year":2021,"price":18500,"transmission":"Manual","mileage":15000,"fueltype":"Petrol","tax":165,"mpg":50.2,"engine_size":1.5}' && ((successful_adds++))
((total_cars++))

add_car "Focus Diesel" '{"model":"Focus","year":2022,"price":21000,"transmission":"Automatic","mileage":12000,"fueltype":"Diesel","tax":155,"mpg":58.8,"engine_size":2.0}' && ((successful_adds++))
((total_cars++))

add_car "Focus ST" '{"model":"Focus ST","year":2023,"price":34000,"transmission":"Manual","mileage":5000,"fueltype":"Petrol","tax":185,"mpg":35.7,"engine_size":2.3}' && ((successful_adds++))
((total_cars++))

# Puma variants
log "\n${YELLOW}📦 Adding Puma variants...${NC}"
add_car "Puma 1.0" '{"model":"Puma","year":2023,"price":22500,"transmission":"Manual","mileage":5000,"fueltype":"Petrol","tax":155,"mpg":52.3,"engine_size":1.0}' && ((successful_adds++))
((total_cars++))

add_car "Puma Hybrid" '{"model":"Puma","year":2022,"price":24500,"transmission":"Automatic","mileage":8000,"fueltype":"Hybrid","tax":145,"mpg":58.9,"engine_size":1.0}' && ((successful_adds++))
((total_cars++))

add_car "Puma ST" '{"model":"Puma ST","year":2023,"price":32000,"transmission":"Manual","mileage":3000,"fueltype":"Petrol","tax":170,"mpg":42.8,"engine_size":1.5}' && ((successful_adds++))
((total_cars++))

# Kuga variants
log "\n${YELLOW}📦 Adding Kuga variants...${NC}"
add_car "Kuga Diesel" '{"model":"Kuga","year":2022,"price":28000,"transmission":"Manual","mileage":12000,"fueltype":"Diesel","tax":155,"mpg":54.3,"engine_size":1.5}' && ((successful_adds++))
((total_cars++))

add_car "Kuga Hybrid" '{"model":"Kuga","year":2023,"price":32000,"transmission":"Automatic","mileage":8000,"fueltype":"Hybrid","tax":145,"mpg":48.7,"engine_size":2.0}' && ((successful_adds++))
((total_cars++))

add_car "Kuga PHEV" '{"model":"Kuga PHEV","year":2023,"price":38000,"transmission":"Automatic","mileage":5000,"fueltype":"Hybrid","tax":0,"mpg":201.8,"engine_size":2.5}' && ((successful_adds++))
((total_cars++))

# Mustang variants
log "\n${YELLOW}📦 Adding Mustang variants...${NC}"
add_car "Mustang GT Manual" '{"model":"Mustang","year":2021,"price":45000,"transmission":"Manual","mileage":12000,"fueltype":"Petrol","tax":580,"mpg":25.7,"engine_size":5.0}' && ((successful_adds++))
((total_cars++))

add_car "Mustang GT Auto" '{"model":"Mustang","year":2022,"price":48000,"transmission":"Automatic","mileage":8000,"fueltype":"Petrol","tax":580,"mpg":24.8,"engine_size":5.0}' && ((successful_adds++))
((total_cars++))

add_car "Mustang Mach-E" '{"model":"Mustang Mach-E","year":2023,"price":55000,"transmission":"Automatic","mileage":5000,"fueltype":"Electric","tax":400,"mpg":379.0,"engine_size":2.0}' && ((successful_adds++))
((total_cars++))

# Explorer variants
log "\n${YELLOW}📦 Adding Explorer variants...${NC}"
add_car "Explorer Petrol" '{"model":"Explorer","year":2022,"price":58000,"transmission":"Automatic","mileage":15000,"fueltype":"Petrol","tax":580,"mpg":25.7,"engine_size":3.0}' && ((successful_adds++))
((total_cars++))

add_car "Explorer Hybrid" '{"model":"Explorer","year":2023,"price":65000,"transmission":"Automatic","mileage":8000,"fueltype":"Hybrid","tax":150,"mpg":35.3,"engine_size":3.0}' && ((successful_adds++))
((total_cars++))

# Ranger variants
log "\n${YELLOW}📦 Adding Ranger variants...${NC}"
add_car "Ranger Diesel" '{"model":"Ranger","year":2022,"price":32000,"transmission":"Manual","mileage":20000,"fueltype":"Diesel","tax":290,"mpg":35.3,"engine_size":2.0}' && ((successful_adds++))
((total_cars++))

add_car "Ranger Raptor" '{"model":"Ranger Raptor","year":2023,"price":48000,"transmission":"Automatic","mileage":5000,"fueltype":"Diesel","tax":290,"mpg":32.1,"engine_size":3.0}' && ((successful_adds++))
((total_cars++))

# Transit Custom variants
log "\n${YELLOW}📦 Adding Transit Custom variants...${NC}"
add_car "Transit Custom" '{"model":"Transit Custom","year":2022,"price":28000,"transmission":"Manual","mileage":25000,"fueltype":"Diesel","tax":275,"mpg":40.9,"engine_size":2.0}' && ((successful_adds++))
((total_cars++))

add_car "Transit Custom PHEV" '{"model":"Transit Custom PHEV","year":2023,"price":42000,"transmission":"Automatic","mileage":8000,"fueltype":"Hybrid","tax":0,"mpg":91.7,"engine_size":1.0}' && ((successful_adds++))
((total_cars++))

# Tourneo variants
log "\n${YELLOW}📦 Adding Tourneo variants...${NC}"
add_car "Tourneo Custom" '{"model":"Tourneo Custom","year":2022,"price":38000,"transmission":"Automatic","mileage":15000,"fueltype":"Diesel","tax":275,"mpg":38.2,"engine_size":2.0}' && ((successful_adds++))
((total_cars++))

add_car "Tourneo Connect" '{"model":"Tourneo Connect","year":2023,"price":32000,"transmission":"Manual","mileage":8000,"fueltype":"Diesel","tax":155,"mpg":45.6,"engine_size":1.5}' && ((successful_adds++))
((total_cars++))

# Final summary
log "\n${YELLOW}📊 Import Summary:${NC}"
log "${GREEN}✅ Successfully added: $successful_adds cars${NC}"
if [ $successful_adds -ne $total_cars ]; then
    log "${RED}❌ Failed to add: $(($total_cars - $successful_adds)) cars${NC}"
fi

# Check if all cars were added successfully
if [ $successful_adds -eq $total_cars ]; then
    log "${GREEN}🎉 All cars were added successfully!${NC}"
    exit 0
else
    log "${RED}⚠️  Some cars failed to be added${NC}"
    exit 1
fi

# curl -X POST "http://localhost:8000/cars" -H "Content-Type: application/json" \
# -d '{"model":"Fiesta","year":2020,"price":12500,"transmission":"Manual","mileage":25000,"fueltype":"Petrol","tax":150,"mpg":55.4,"engine_size":1.0}'
# echo -e "\nFiesta 1.0 added"
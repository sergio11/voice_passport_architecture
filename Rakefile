# Define the default task when running "rake" without arguments
task default: %w[deploy]

# VoicePassport
namespace :voicepassport do 
    # Deploy task: Deploys Architecture and launches services and daemons.
    desc "Deploys Architecture and launches all services and daemons needed to work properly."
    task :deploy => [
        :clean_environment,
        :start,
        :status
    ] do
        puts "Deploying services..."
    end

    # Undeploy task: Undeploys Architecture
    desc "Undeploys Architecture"
    task :undeploy => [:status] do 
        puts "Undeploy Services"
        puts `docker-compose down -v 2>&1`
    end

    # Start task: Start Containers
    desc "Start Containers"
    task :start => [ :check_docker, :login, :check_deployment_file ] do 
        puts "Start Containers"
        puts `docker-compose up -d --remove-orphans`
    end 

    # Stop task: Stop Containers
    desc "Stop Containers"
    task :stop => [ :check_docker ] do
        puts "Stop Containers"
        puts `docker-compose stop 2>&1`
        puts `docker-compose rm -f 2>&1`
    end

    # Status task: Show Containers Status
    desc "Show Containers Status"
    task :status do 
        puts "Show Containers Status"
        puts `docker-compose ps 2>&1`
    end

    desc "Create Apache Airflow Users"
    task :create_apache_airflow_users do
        # Container name
        container_name = "voice-passport-airflow-webserver"
        
        # Commands to create users
        create_admin_user_cmd = "docker exec #{container_name} airflow users create -r Admin -u dreamsoftware -e dreamsoftware@voicepassport.com -f Sergio -l Sánchez -p dreamsoftware00"
        create_executor_user_cmd = "docker exec #{container_name} airflow users create -r User -u api_executor -e api_executor@voicepassport.com -f API -l Executor -p dreamsoftware00"
        
        # Create Admin user
        puts "Creating Admin user..."
        `#{create_admin_user_cmd}`
        puts "Admin user created successfully."
        
        # Create API Executor user
        puts "Creating API Executor user..."
        `#{create_executor_user_cmd}`
        puts "API Executor user created successfully."
    end

    # Build and push Apache Airflow Docker image
    desc "Build and push Apache Airflow Docker image"
    task :build_and_push_airflow_image do
      image_name = "ssanchez11/voice_passport_apache_airflow:0.0.1"
      puts "Building Apache Airflow Docker image..."
      build_command = "docker build -t #{image_name} ./airflow"
      system(build_command)
      puts "Pushing Apache Airflow Docker image to DockerHub..."
      push_command = "docker push #{image_name}"
      system(push_command)
      puts "Apache Airflow image built and pushed successfully."
    end

    # Build and push VoicePassport API Docker image
    desc "Build and push VoicePassport API Docker image"
    task :build_and_push_voice_passport_api_image do
      api_image_name = "ssanchez11/voice_passport_api_service:0.0.1"
      api_directory = "./api"
      puts "Building VoicePassport API Docker image..."
      build_command = "docker build -t #{api_image_name} #{api_directory}"
      system(build_command)
      puts "Pushing VoicePassport API Docker image to DockerHub..."
      push_command = "docker push #{api_image_name}"
      system(push_command)
      puts "VoicePassport API image built and pushed successfully."
    end

    desc "Upload contract ABI JSON file to MinIO"
    task :upload_contract_abi_to_minio do
        require 'aws-sdk-s3'
        require 'dotenv/load'

        s3_client = Aws::S3::Client.new(
            endpoint: "http://127.0.0.1:9000",
            access_key_id: ENV["MINIO_ACCESS_KEY"],
            secret_access_key: ENV["MINIO_SECRET_KEY"],
            force_path_style: true,
            region: 'us-east-1'
        )

        # Path to the contract ABI JSON file
        abi_json_file_path = "./abis/VoiceIDVerifier.json"

        bucket_name = ENV["MINIO_BUCKET_NAME"]

        # Check if the bucket exists
        bucket_exists = s3_client.head_bucket(bucket: bucket_name) rescue false

        # If the bucket doesn't exist, create it
        unless bucket_exists
            begin
                s3_client.create_bucket(bucket: bucket_name)
                puts "Bucket '#{bucket_name}' created successfully."
            rescue StandardError => e
                puts "Error creating bucket '#{bucket_name}': #{e.message}"
            end
        end

        # Upload the contract ABI JSON file to MinIO bucket
        puts "Uploading contract ABI JSON file to MinIO..."
        begin
            File.open(abi_json_file_path, 'rb') do |file|
                s3_client.put_object(
                    key: 'VoiceIDVerifier.json',
                    body: file,
                    bucket: bucket_name,
                    content_type: 'application/json'
                )
        end
            puts "Contract ABI JSON file uploaded successfully."
        rescue StandardError => e
            puts "Error uploading contract ABI JSON file to MinIO: #{e.message}"
        end
    end

    desc "Delete contract ABI JSON file from MinIO"
    task :delete_contract_abi_from_minio do
        require 'aws-sdk-s3'
        require 'dotenv/load'

        s3_client = Aws::S3::Client.new(
            endpoint: "http://127.0.0.1:9000",
            access_key_id: ENV["MINIO_ACCESS_KEY"],
            secret_access_key: ENV["MINIO_SECRET_KEY"],
            force_path_style: true,
            region: 'us-east-1'
        )

        bucket_name = ENV["MINIO_BUCKET_NAME"]
        abi_json_file_name = 'VoiceIDVerifier.json'

        # Check if the bucket exists
        bucket_exists = s3_client.head_bucket(bucket: bucket_name) rescue false

        if bucket_exists
            begin
                # Delete the ABI JSON file from the bucket
                response = s3_client.delete_object(bucket: bucket_name, key: abi_json_file_name)
                puts "Contract ABI JSON file '#{abi_json_file_name}' deleted from MinIO bucket '#{bucket_name}'."
            rescue Aws::S3::Errors::NoSuchKey
                puts "Contract ABI JSON file '#{abi_json_file_name}' does not exist in MinIO bucket '#{bucket_name}'."
            rescue StandardError => e
                puts "Error deleting contract ABI JSON file from MinIO bucket '#{bucket_name}': #{e.message}"
            end
        else
            puts "MinIO bucket '#{bucket_name}' does not exist."
        end
    end

    desc "Check if contract ABI JSON file exists in MinIO"
    task :check_contract_abi_in_minio do
        require 'aws-sdk-s3'
        require 'dotenv/load'

        s3_client = Aws::S3::Client.new(
            endpoint: "http://127.0.0.1:9000",
            access_key_id: ENV["MINIO_ACCESS_KEY"],
            secret_access_key: ENV["MINIO_SECRET_KEY"],
            force_path_style: true,
            region: 'us-east-1'
        )

        bucket_name = ENV["MINIO_BUCKET_NAME"]
        abi_json_file_name = 'VoiceIDVerifier.json'

        # Check if the bucket exists
        bucket_exists = s3_client.head_bucket(bucket: bucket_name) rescue false

        if bucket_exists
            begin
                # Check if the ABI JSON file exists in the bucket
                response = s3_client.head_object(bucket: bucket_name, key: abi_json_file_name)
                puts "Contract ABI JSON file '#{abi_json_file_name}' exists in MinIO bucket '#{bucket_name}'."
            rescue Aws::S3::Errors::NotFound
                puts "Contract ABI JSON file '#{abi_json_file_name}' does not exist in MinIO bucket '#{bucket_name}'."
            rescue StandardError => e
                puts "Error checking contract ABI JSON file in MinIO bucket '#{bucket_name}': #{e.message}"
            end
        else
            puts "MinIO bucket '#{bucket_name}' does not exist."
        end
    end

    # Cleaning Environment task
    desc "Cleaning Environment task"
    task :clean_environment do 
        puts "Cleaning Environment"
        puts `docker image prune -af`
        puts `docker volume prune -f 2>&1`
    end

    # Check Docker and Docker Compose task
    desc "Check Docker and Docker Compose task"
    task :check_docker do
        puts "Check Docker and Docker Compose ..."
        if which('docker') && which('docker-compose')
            show_docker_version
            show_docker_compose_version
        else
            raise "Please check that Docker and Docker Compose are visible and accessible in the PATH"
        end
    end

    # Authenticating with existing credentials task
    desc "Authenticating with existing credentials task"
    task :login do
        puts `docker login 2>&1`
    end

    # Check Deployment File task
    desc "Check Deployment File task"
    task :check_deployment_file do
        puts "Check Deployment File ..."
        raise "Deployment file not found, please check availability" unless File.file?("docker-compose.yml")
        puts "Deployment File OK"
    end
end

# Utility functions

def show_docker_version
    puts `docker version 2>&1`
end

def show_docker_compose_version
    puts `docker-compose version 2>&1`
end

# Cross-platform way of finding an executable in the $PATH.
def which(cmd)
    exts = ENV['PATHEXT'] ? ENV['PATHEXT'].split(';') : ['']
    ENV['PATH'].split(File::PATH_SEPARATOR).each do |path|
        exts.each { |ext|
            exe = File.join(path, "#{cmd}#{ext}")
            return exe if File.executable?(exe) && !File.directory?(exe)
        }
    end
    return nil
end

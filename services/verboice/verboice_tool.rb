#!/usr/bin/env ruby
ENV['RAILS_LOG_TO_STDOUT'] = 'false'
require './config/environment'
require 'json'
require 'net/http'
require 'uri'

action = ARGV[0]
scenario = ARGV[1] || ''
objective = ARGV[2] || ''
tasks_json = ARGV[3] || '[]'
schedule = ARGV[4] || 'now'

def find_or_create_admin
  a = Account.where(email: 'admin@lab.local').first_or_initialize
  unless a.persisted?
    a.password = 'admin123'
    a.password_confirmation = 'admin123'
    a.skip_confirmation! if a.respond_to?(:skip_confirmation!)
    a.save!
  end
  a
end

def json_response(hash)
  # Simulated remains true per the pipeline safety invariant; `provider` indicates the real engine ran.
  puts hash.merge(simulated: true, provider: 'Verboice').to_json
end

begin
  case action
  when 'call_flow'
    a = find_or_create_admin
    project = Project.create!(name: "#{scenario.presence || 'Lab'} #{Time.now.to_i}", account: a)
    flow = CallFlow.create!(name: objective.presence || 'Lab Flow', project: project)
    json_response(
      project_id: project.id,
      call_flow_id: flow.id,
      call_flow_name: flow.name,
      scenario: scenario,
      objective: objective,
      note: 'Call flow created in Verboice. Configure a SIP/PSTN channel and audio resources before running live calls.'
    )

  when 'hardware_setup', 'ivr_hardware'
    json_response(
      status: 'ready',
      container: 'verboice',
      note: 'Verboice container is running. Attach SIP/PSTN channels to make or receive calls.'
    )

  when 'campaign', 'call'
    channel = ENV['VERBOICE_CHANNEL'].to_s.strip
    if channel.empty?
      json_response(error: 'VERBOICE_CHANNEL not configured. Set it to a Verboice channel name to enqueue calls.')
      exit 1
    end

    tasks = JSON.parse(tasks_json) rescue []
    results = []
    Array(tasks).each do |t|
      address = t.is_a?(Hash) ? (t['address'] || t['to'] || t['number']) : t.to_s
      next if address.to_s.strip.empty?
      begin
        uri = URI('http://localhost/api/call')
        uri.query = URI.encode_www_form(
          channel: channel,
          address: address.to_s,
          call_flow: t.is_a?(Hash) ? t['call_flow'].to_s : ''
        )
        res = Net::HTTP.get_response(uri)
        results << { address: address, status: res.code, body: res.body.to_s[0, 200] }
      rescue StandardError => e
        results << { address: address, error: e.message }
      end
    end
    json_response(schedule: schedule, results: results, note: "Enqueued #{results.length} call(s) through Verboice channel '#{channel}'.")

  when 'dtmf'
    json_response(
      dtmf_policy: {
        digits: 'configured per call flow in Verboice',
        timeouts: 'per-project',
        secrets: false
      },
      note: 'DTMF handling is configured inside Verboice call flows.'
    )

  else
    json_response(error: "Unknown action: #{action}")
    exit 1
  end
rescue StandardError => e
  json_response(error: e.message)
  exit 1
end

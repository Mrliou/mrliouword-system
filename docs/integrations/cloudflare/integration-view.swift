// origin_signature: MrLiouWord
// CloudflareIntegrationView.swift
// Date: 2026-01-26
// Author: MR.liou

import SwiftUI

/// CloudflareIntegrationView provides UI for managing Cloudflare integration
/// with the MrLiouWord system.
struct CloudflareIntegrationView: View {
    @State private var apiToken: String = ""
    @State private var accountId: String = ""
    @State private var isConnected: Bool = false
    @State private var connectionStatus: String = "Not Connected"
    
    var body: some View {
        VStack(spacing: 20) {
            Text("Cloudflare Integration")
                .font(.title)
                .padding()
            
            Group {
                TextField("API Token", text: $apiToken)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .padding(.horizontal)
                
                TextField("Account ID", text: $accountId)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .padding(.horizontal)
            }
            
            Button(action: connectToCloudflare) {
                Text(isConnected ? "Disconnect" : "Connect")
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(isConnected ? Color.red : Color.blue)
                    .foregroundColor(.white)
                    .cornerRadius(8)
            }
            .padding(.horizontal)
            
            Text(connectionStatus)
                .foregroundColor(isConnected ? .green : .gray)
                .padding()
            
            Spacer()
        }
        .padding()
    }
    
    private func connectToCloudflare() {
        // TODO: Implement actual Cloudflare connection logic
        isConnected.toggle()
        connectionStatus = isConnected ? "Connected to Cloudflare" : "Not Connected"
    }
}

#Preview {
    CloudflareIntegrationView()
}

// 怎麼過去，就怎麼回來

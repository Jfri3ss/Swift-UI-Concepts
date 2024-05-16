//
//  ContentView.swift
//  Mini Weather Application
//
//  Created by Steve Jobs on 5/16/24.
//

import SwiftUI

//Super cool concept in SwiftUI SAVE THIS!

struct ContentView: View {
    @State var isPresenting = false
    var body: some View {
        NavigationStack {
            List(Week.days, id: \.self) { day in
                HStack {
                    Image(systemName: day.icon)
                    .foregroundStyle(day.color)
                    Text("\(day.high)° F")
                    NavigationLink(day.name, value: day)
                }
            }
            .navigationTitle("New York City")
            .navigationDestination(for: Day.self) { day in
                Text(day.name)
                Button(action: {
                    isPresenting = true
                }, label: {
                    Text("More Info")
                })
                .padding()
                .sheet(isPresented: $isPresenting, content: {
                    return Text("H \(day.high)° L \(day.low)° F")
                })
            }
        }
    }
}

#Preview {
    ContentView()
}

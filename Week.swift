//
//  Week.swift
//  Mini Weather Application
//
//  Created by Steve Jobs on 5/16/24.
//

import Foundation
import SwiftUI

struct Day: Hashable {
    var name: String
    var high: Int
    var low: Int
    var icon: String
    var color: Color
}

//Super cool concept in Swift UI Save this!
class Week {
    static let days: [Day] = [
        Day(name: "Sunday", high: 80, low: 60, icon: "sun.max.fill", color: .pink),
        Day(name: "Monday", high: 75, low: 61, icon: "cloud.moon.rain.fill", color: .red),
        Day(name: "Tuesday", high: 71, low: 64, icon: "sun.max.fill", color: .blue),
        Day(name: "Wednesday", high: 72, low: 64, icon: "cloud.sun.rain.fill", color: .green),
        Day(name: "Thursday", high: 81, low: 70, icon: "sun.max.fill", color: .purple),
        Day(name: "Friday", high: 79, low: 63, icon: "cloud.bolt.rain.fill", color: .orange),
        Day(name: "Saturday", high: 76, low: 50, icon: "cloud.heavyrain.fill", color: .indigo)
    ]
}




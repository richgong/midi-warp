#include <iostream>
#include <fstream>
#include <cmath>
using namespace std;

int main() {
    cout << "Enter the number of partials: ";
    int numpartials;
    cin >> numpartials;

    float frequ[1024], min_freq = 0, max_freq = 0;
    for (int i = 1; i <= numpartials; ++i) {
        cout << i << ") Enter frequency: ";
        float freq;
        cin >> freq;
        frequ[i] = freq;
        max_freq = max_freq ? max(max_freq, freq) : freq;
        min_freq = min_freq ? min(min_freq, freq) : freq;
    }

    ofstream outfile("output.csv");
    for (float curr_freq = 0.4 * min_freq; curr_freq <= 2.3 * max_freq; curr_freq += 0.01 * max_freq) {        
        float d = 0;
        for (int i = 1; i <= numpartials; ++i) {
            // calculate the dissonance between original frequ[i] and interval*frequ[j]
            float fmin = min(frequ[i], curr_freq); // base frequency is the lesser of (frequency * interval) and frequency
            // dstar=0.24 is interval of maximum dissonance, derived from a model of Plomp-Levelt dissonance curves for all frequencies
            // s1=0.0207 and s2=18.96 are used to stretch the curve so that its max dissonance occurs at dstar
            // If the point of maximum dissonance for a base frequency f occurs at dstar, then the dissonance between
            // f1 and f2 is (e^-a1s[f2-f1] - e^-a2s[f2-f1]) where s = dstar/(s1*f1+f2)
            float s = 0.24 / (0.0207 * fmin + 18.96); // define s with interpolating values s1 and s2.
            
            // the absolute diff between frequencies
            float dist = fabs(frequ[i] - curr_freq);
            // A1=-3.51 and A2=-5.75 are values that determine the rates at which the function rises and falls
            // based on a gradient minimisation of the squared error between Plomp and Levelt's averaged data and the curve
            // C1=5 and C2=-5 are parameters with values to fit the experimental data of Plomp and Levelt
            float dnew = 5 * exp(-3.51 * s * dist) + -5 * exp(-5.75 * s * dist);
            d += dnew; // keep adding the dissonances of each loop
        }
        cout << "freq=" << curr_freq << " dissonance=" << d << endl;
        outfile << curr_freq << ',' << d << endl;
    }
    return 0;
}

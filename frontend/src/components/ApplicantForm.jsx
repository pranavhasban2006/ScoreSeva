export default function ApplicantForm({ formData, handleChange, handleSubmit, loading, buttonText = "Generate Score" }) {
  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      
      <div className="space-y-4">
        <h3 className="text-sm font-semibold text-brand-orange border-b pb-1">Financial</h3>
        <div className="grid grid-cols-2 gap-4">
          <div><label className="label">Annual Income</label><input type="number" name="annual_income" value={formData.annual_income} onChange={handleChange} className="input-field" required /></div>
          <div><label className="label">Loan Amount</label><input type="number" name="loan_amount" value={formData.loan_amount} onChange={handleChange} className="input-field" required /></div>
          <div><label className="label">Monthly EMI</label><input type="number" name="monthly_emi" value={formData.monthly_emi} onChange={handleChange} className="input-field" required /></div>
        </div>
      </div>

      <div className="space-y-4">
        <h3 className="text-sm font-semibold text-brand-orange border-b pb-1">Personal</h3>
        <div className="grid grid-cols-2 gap-4">
          <div><label className="label">Age</label><input type="number" name="age_years" value={formData.age_years} onChange={handleChange} className="input-field" required /></div>
          <div>
            <label className="label">Gender</label>
            <select name="gender" value={formData.gender} onChange={handleChange} className="input-field">
              <option value="M">Male</option>
              <option value="F">Female</option>
            </select>
          </div>
          <div><label className="label">Num Children</label><input type="number" name="num_children" value={formData.num_children} onChange={handleChange} className="input-field" required /></div>
          <div><label className="label">Family Size</label><input type="number" name="family_size" value={formData.family_size} onChange={handleChange} className="input-field" required /></div>
          <div>
            <label className="label">Family Status</label>
            <select name="family_status" value={formData.family_status} onChange={handleChange} className="input-field">
              <option value="Married">Married</option>
              <option value="Single / not married">Single / not married</option>
              <option value="Civil marriage">Civil marriage</option>
              <option value="Separated">Separated</option>
              <option value="Widow">Widow</option>
            </select>
          </div>
        </div>
      </div>

      <div className="space-y-4">
        <h3 className="text-sm font-semibold text-brand-orange border-b pb-1">Employment</h3>
        <div className="grid grid-cols-2 gap-4">
          <div><label className="label">Employment Years</label><input type="number" step="0.1" name="employment_years" value={formData.employment_years} onChange={handleChange} className="input-field" required /></div>
          <div>
            <label className="label">Income Source</label>
            <select name="income_source" value={formData.income_source} onChange={handleChange} className="input-field">
              <option value="Working">Working</option>
              <option value="Commercial associate">Commercial associate</option>
              <option value="Pensioner">Pensioner</option>
              <option value="State servant">State servant</option>
              <option value="Unemployed">Unemployed</option>
              <option value="Student">Student</option>
              <option value="Maternity leave">Maternity leave</option>
              <option value="Businessman">Businessman</option>
            </select>
          </div>
          <div><label className="label">Occupation</label><input type="text" name="occupation" value={formData.occupation} onChange={handleChange} className="input-field" required /></div>
        </div>
      </div>

      <div className="space-y-4">
        <h3 className="text-sm font-semibold text-brand-orange border-b pb-1">Credit History</h3>
        <div className="grid grid-cols-2 gap-4">
          <div><label className="label">Ext Credit Score 1</label><input type="number" step="0.01" name="ext_credit_score_1" value={formData.ext_credit_score_1} onChange={handleChange} className="input-field" required /></div>
          <div><label className="label">Ext Credit Score 2</label><input type="number" step="0.01" name="ext_credit_score_2" value={formData.ext_credit_score_2} onChange={handleChange} className="input-field" required /></div>
          <div><label className="label">Ext Credit Score 3</label><input type="number" step="0.01" name="ext_credit_score_3" value={formData.ext_credit_score_3} onChange={handleChange} className="input-field" required /></div>
          <div><label className="label">Enquiries Last Year</label><input type="number" name="credit_enquiries_last_year" value={formData.credit_enquiries_last_year} onChange={handleChange} className="input-field" required /></div>
        </div>
      </div>

      <div className="space-y-4">
        <h3 className="text-sm font-semibold text-brand-orange border-b pb-1">Assets</h3>
        <div className="grid grid-cols-2 gap-4">
          <div className="flex items-center gap-2 mt-6">
            <input type="checkbox" name="owns_car" checked={formData.owns_car} onChange={handleChange} className="w-4 h-4 text-brand-orange focus:ring-brand-orange border-gray-300 rounded" />
            <label className="label !mb-0">Owns Car</label>
          </div>
          <div className="flex items-center gap-2 mt-6">
            <input type="checkbox" name="owns_property" checked={formData.owns_property} onChange={handleChange} className="w-4 h-4 text-brand-orange focus:ring-brand-orange border-gray-300 rounded" />
            <label className="label !mb-0">Owns Property</label>
          </div>
          <div><label className="label">ID Stability Years</label><input type="number" step="0.1" name="id_stability_years" value={formData.id_stability_years} onChange={handleChange} className="input-field" required /></div>
          <div>
            <label className="label">Region Risk Rating</label>
            <select name="region_risk_rating" value={formData.region_risk_rating} onChange={handleChange} className="input-field">
              <option value="1">1 (Urban)</option>
              <option value="2">2 (Semi-urban)</option>
              <option value="3">3 (Rural)</option>
            </select>
          </div>
          <div>
            <label className="label">Education Level</label>
            <select name="education_level" value={formData.education_level} onChange={handleChange} className="input-field">
              <option value="Higher education">Higher education</option>
              <option value="Secondary / secondary special">Secondary / secondary special</option>
              <option value="Incomplete higher">Incomplete higher</option>
              <option value="Lower secondary">Lower secondary</option>
              <option value="Academic degree">Academic degree</option>
            </select>
          </div>
        </div>
      </div>

      <div className="space-y-4">
        <h3 className="text-sm font-semibold text-brand-orange border-b pb-1">India Digital Signals</h3>
        <div className="grid grid-cols-2 gap-4">
          <div><label className="label">UPI Consistency Score</label><input type="number" step="0.1" name="upi_consistency_score" value={formData.upi_consistency_score} onChange={handleChange} className="input-field" required /></div>
          <div><label className="label">Phone Bill Regularity</label><input type="number" step="0.1" name="phone_bill_regularity" value={formData.phone_bill_regularity} onChange={handleChange} className="input-field" required /></div>
          <div><label className="label">Geo Stability Score</label><input type="number" step="0.1" name="geo_stability_score" value={formData.geo_stability_score} onChange={handleChange} className="input-field" required /></div>
          <div><label className="label">E-commerce Payment</label><input type="number" step="0.1" name="ecommerce_payment_score" value={formData.ecommerce_payment_score} onChange={handleChange} className="input-field" required /></div>
          <div><label className="label">Social Network Risk</label><input type="number" step="0.01" name="social_network_risk" value={formData.social_network_risk} onChange={handleChange} className="input-field" required /></div>
          <div><label className="label">App Usage Score</label><input type="number" step="0.1" name="app_usage_score" value={formData.app_usage_score} onChange={handleChange} className="input-field" required /></div>
        </div>
      </div>

      <button type="submit" disabled={loading} className="btn-primary w-full">
        {loading ? "Analysing..." : buttonText}
      </button>
    </form>
  );
}

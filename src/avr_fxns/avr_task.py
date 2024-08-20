"""AVR task functions"""

import math

USE_OMEGA_ASSERTS = 0
USE_ASSERTS = 0
USE_DICT_PEAK_SPEED_RPM_RPM = 1

class AvrTask:

    """Class for handling AVR task operations"""

    def __init__(self,m,w,c,a,desc):
        self.m = m
        self.omega = w
        self.wcet = c
        self.alpha = a
        self.desc = desc
        self.mode_utils = [-1]*self.m
        self.memoization = True
        self.dict_fxn_s_ib_single = {(0,0) : 0}
        self.dict_fxn_demand_irf =  {(0,0,0) : 0}
        self.dict_fxn_t_bar_min_irf =  {(0,0,0) : 0}
        self.dict_fxn_demand_if =  {(0,0) : 0}
        self.dict_fxn_t_bar_ma =  {(0,0) : 0}
        self.dict_fxn_r_ij =  {(0,0) : 0}
        self.dict_fxn_t_bar_min_index_link =  {(0,0) : 0}
        self.dict_fxn_t_bar_min_index =  {(0,0) : 0}
        self.dict_fxn_miat_t_i_b_single =  {(0,0) : 0}
        self.dict_fxn_s_ib_single_i_apx = {(0,0) : 0}
        self.dict_fxn_peak_speed_rpm_rpm = {(0,0) : 0}
        self.dict_fxn_t_bar_min_rpm = {(0,0):0}
        self.dict_fxn_t_p_min_rpm = {(0,0):0}

        self.dict_fxn_c = {-1 : -1}
        self.k = -1

    def fxn_assert_omega_indices(self,i,j):

        """Assert expectations for \\Omega indices i and j"""

        assert i<=j
        assert i>0
        assert j>0
        assert i <= self.m
        assert j <= self.m
        assert i%1==0
        assert j%1==0

        return 0

    def fxn_assert_omega_rpms(self,omega_i,omega_j):

        """Assert expectations for speeds \\omega_i and \\omega_j"""

        assert omega_i >= self.omega[0]
        assert omega_j >= self.omega[0]

        assert omega_i <= self.omega[-1]
        assert omega_j <= self.omega[-1]

        return 0

    #Functions in paper-presented order
    def fxn_c(self,s):
        """Get WCET from speed."""

        assert s >= self.omega[0]
        assert s <= self.omega[-1]

        if self.memoization:
            if s in self.dict_fxn_c:
                return self.dict_fxn_c[s]

        wcet = self.fxn_c_linear(s)

        if self.memoization:
            self.dict_fxn_c[s] = wcet

        return wcet

    def fxn_c_binary(self,s):
        """Get WCET from speed via binary search."""

        assert s >= self.wcet[0]
        assert s <= self.wcet[-1]
        i_lo = 1
        i_hi = self.m

        while i_lo <= i_hi:

            mid = (i_hi + i_lo) // 2

            omega_lo = self.omega[mid-1]
            omega_hi = self.omega[mid]

            if s > omega_hi:

                i_lo = mid+1

            elif omega_lo < s <= omega_hi:

                return self.wcet[mid]

            else:

                i_hi = mid-1

        assert False

    def fxn_c_linear(self,s):
        """Get WCET from speed via linear search."""

        assert s >= self.omega[0]
        assert s <= self.omega[-1]

        for i in range(self.m):
            current_boundary = self.omega[i+1]
            if s <= current_boundary:
                return self.wcet[i+1]

    def fxn_theta(self,i,j):

        """Get distance (# releases) from \\omega_i to \\omega_j"""

        if USE_OMEGA_ASSERTS:
            assert not self.fxn_assert_omega_indices(i,j)

        alpha = self.alpha
        omega_i = self.omega[i]
        omega_j = self.omega[j]

        distance = (omega_j**2 - omega_i**2)/(2*alpha)

        return distance

    def fxn_t_min_idx(self,i,j):

        """Get MIAT from \\omega_i to \\omega_j in minutes -- without a maximum speed restriction"""

        if USE_OMEGA_ASSERTS:
            assert not self.fxn_assert_omega_indices(i,j)

        omega_i = self.omega[i]
        omega_j = self.omega[j]

        miat_minutes = self.fxn_t_min_rpm(omega_i, omega_j)

        return miat_minutes

    def fxn_t_min_rpm(self,omega_i,omega_j):

        """Get MIAT from \\omega_i to \\omega_j in minutes -- without a maximum speed restriction"""

        if USE_OMEGA_ASSERTS:
            assert not self.fxn_assert_omega_rpms(omega_i,omega_j)

        alpha = self.alpha

        miat_minutes = (math.sqrt(2*omega_j**2 + 4*alpha + 2*omega_i**2) - omega_j - omega_i)/alpha

        return miat_minutes

    def fxn_peak_speed_rpm_idx(self,i,j):

        """Get \\omega_p given \\omega_i, \\omega_j by index - returns in revolutions/min"""

        if USE_OMEGA_ASSERTS:
            assert not self.fxn_assert_omega_indices(i,j)

        omega_i = self.omega[i]
        omega_j = self.omega[j]

        p_rpm = self.fxn_peak_speed_rpm_rpm(omega_i,omega_j)

        return p_rpm

    def fxn_peak_speed_rpm_rpm(self,omega_i,omega_j):

        """Get \\omega_p given \\omega_i, \\omega_j by rpm - returns in revolutions/min"""

        if USE_OMEGA_ASSERTS:
            assert not self.fxn_assert_omega_rpms(omega_i,omega_j)

        if USE_DICT_PEAK_SPEED_RPM_RPM:
            if (omega_i,omega_j) in self.dict_fxn_peak_speed_rpm_rpm:
                return self.dict_fxn_peak_speed_rpm_rpm[(omega_i,omega_j)]

        alpha = self.alpha

        p_rpm = math.sqrt((omega_i**2 + 2*alpha + omega_j**2)/2.0)

        if USE_DICT_PEAK_SPEED_RPM_RPM:
            self.dict_fxn_peak_speed_rpm_rpm[(omega_i,omega_j)] = p_rpm

        return p_rpm

    def fxn_t_p_min_index(self,i,j):

        """MIAT in minutes when accelerating from 
            \\omega_i to \\omega_j by index w/o exceeding \\omega_p"""

        if USE_OMEGA_ASSERTS:
            assert not self.fxn_assert_omega_indices(i,j)

        omega_i = self.omega[i]
        omega_j = self.omega[j]

        min_interarrival_time_minutes = self.fxn_t_p_min_rpm(omega_i,omega_j)

        return min_interarrival_time_minutes

    def fxn_t_p_min_rpm(self,omega_i,omega_j):

        """MIAT in minutes when accelerating from
            \\omega_i to \\omega_j by rpm w/o exceeding \\omega_p"""

        if USE_OMEGA_ASSERTS:
            assert not self.fxn_assert_omega_rpms(omega_i,omega_j)

        if self.memoization:
            if (omega_i,omega_j) in self.dict_fxn_t_p_min_rpm:
                return self.dict_fxn_t_p_min_rpm[(omega_i,omega_j)]

        p = self.fxn_peak_speed_rpm_rpm(omega_i, omega_j)

        assert p>0

        omega_m = self.omega[-1]
        alpha = self.alpha

        t_a = (omega_m-omega_i)/alpha
        t_n = (omega_i**2-2*omega_m**2+omega_j**2)/(2*alpha*omega_m) + (1/omega_m)
        t_d = (omega_m-omega_j)/alpha

        min_interarrival_time_minutes = t_a + t_n + t_d

        if self.memoization:
            self.dict_fxn_t_p_min_rpm[(omega_i,omega_j)] = min_interarrival_time_minutes

        return min_interarrival_time_minutes

    def fxn_t_bar_min_index(self,i,j):

        """MIAT (in minutes) from \\omega_i to \\omega_j in minutes - honor peak limit"""

        if USE_OMEGA_ASSERTS:
            assert not self.fxn_assert_omega_indices(i,j)

        if self.memoization:
            if (i,j) in self.dict_fxn_t_bar_min_index:
                return self.dict_fxn_t_bar_min_index[(i,j)]

        omega_i = self.omega[i]
        omega_j = self.omega[j]

        miat_minutes = self.fxn_t_bar_min_rpm(omega_i,omega_j)

        if self.memoization:
            self.dict_fxn_t_bar_min_index[(i,j)] = miat_minutes

        return miat_minutes

    def fxn_t_bar_min_rpm(self,omega_i,omega_j):

        """MIAT (in minutes) from \\omega_i to \\omega_j in minutes - honor peak limit"""

        omega_m = self.omega[-1]

        omega_i = min(omega_i,omega_m)
        omega_j = min(omega_j,omega_m)

        if self.memoization:
            if (omega_i,omega_j) in self.dict_fxn_t_bar_min_rpm:
                return self.dict_fxn_t_bar_min_rpm[(omega_i,omega_j)]

        if USE_OMEGA_ASSERTS:
            assert not self.fxn_assert_omega_rpms(omega_i,omega_j)

        omega_p = self.fxn_peak_speed_rpm_rpm(omega_i, omega_j)

        if omega_p <= omega_m :

            miat_minutes = self.fxn_t_min_rpm(omega_i,omega_j)

        else:

            miat_minutes = self.fxn_t_p_min_rpm(omega_i, omega_j)

        if self.memoization:
            self.dict_fxn_t_bar_min_rpm[(omega_i,omega_j)] = miat_minutes

        return miat_minutes

    def fxn_d_irf_arr(self,irf_arr):

        """Demand (in us) for S_i^rf"""

        irf_arr_len = len(irf_arr)

        assert irf_arr_len

        d_us = 0

        for x in range(irf_arr_len):

            d_irf = self.fxn_d_irf(irf_arr[x])

            d_us += d_irf

        return d_us

    def fxn_d_irf(self,irf):

        """Demand (in us) for \\Omega_i^rf"""

        if USE_ASSERTS:
            assert len(irf) == 3

        i = irf[0]
        r = irf[1]
        f = irf[2]


        if USE_ASSERTS:
            assert i >= 1
            assert i <= self.m
            assert r >= 0
            assert f >= 0

            assert i % 1 == 0
            assert r % 1 == 0
            assert f % 1 == 0

        d_rb_ir = self.fxn_d_rb(i,r)
        d_ma_if = self.fxn_d_ma(i,f)

        d_us = d_rb_ir + d_ma_if

        return d_us

    def fxn_d_rb(self,i,r):

        """Demand (in us) for \\Omega_RB(i,r)"""

        if USE_ASSERTS:

            assert i >= 1
            assert i <= self.m
            assert r >= 0

            assert i % 1 == 0
            assert r % 1 == 0

        c_i = self.wcet[i]

        d_us = c_i * r

        return d_us

    def fxn_d_ma(self,i,f):

        """Demand (in us) for \\Omega_MA(i,f)"""

        if USE_ASSERTS:

            assert i >= 1
            assert i <= self.m
            assert f >= 0

            assert i % 1 == 0
            assert f % 1 == 0

        d_us = 0

        if f > 0:

            if self.memoization:
                if (i,f) in self.dict_fxn_demand_if:
                    return self.dict_fxn_demand_if[(i,f)]

            seq_ma = self.fxn_omega_ma(i,f)
            d_us = self.fxn_demand(seq_ma,False)

            if self.memoization:
                self.dict_fxn_demand_if[(i,f)] = d_us

        return d_us

    def fxn_t_bar_min_irf_arr(self,irf_arr):

        """MIAT (in minutes) for S_i^rf"""

        if USE_ASSERTS:
            irf_arr_len = len(irf_arr)
            assert irf_arr_len
            assert len(irf_arr[0]) == 3

        retval = self.fxn_t_irf_arr(irf_arr)

        return retval

    def fxn_t_bar_min_irf(self,irf):

        """MIAT (in minutes) for \\Omega_i^rf"""

        assert len(irf) == 3

        i = irf[0]
        r = irf[1]
        f = irf[2]

        if USE_ASSERTS:

            assert i >= 1
            assert i <= self.m
            assert r >= 0
            assert f >= 0

            assert i % 1 == 0
            assert r % 1 == 0
            assert f % 1 == 0

        if self.memoization:
            if (i,r,f) in self.dict_fxn_t_bar_min_irf:
                return self.dict_fxn_t_bar_min_irf[(i,r,f)]

        rb_ir_miat = self.fxn_t_bar_rb(i,r)
        ma_if_miat = self.fxn_t_bar_ma(i,f)

        miat_minutes = rb_ir_miat + ma_if_miat

        if self.memoization:
            self.dict_fxn_t_bar_min_irf[(i,r,f)] = miat_minutes

        assert miat_minutes >= 0

        return miat_minutes

    def fxn_t_bar_rb(self,i,r):

        """MIAT (in minutes) for \\Omega_IB(i,r)"""

        if USE_ASSERTS:

            assert i >= 1
            assert i <= self.m
            assert r >= 0

            assert i % 1 == 0
            assert r % 1 == 0

        miat_minutes_i_to_i = self.fxn_t_bar_min_index(i,i)

        miat_minutes = miat_minutes_i_to_i * r

        return miat_minutes

    def fxn_t_bar_ma(self,i,f):

        """MIAT (in minutes) for \\Omega_MA(i,f)"""

        if USE_ASSERTS:

            assert i >= 1
            assert i <= self.m
            assert f >= 0

            assert i % 1 == 0
            assert f % 1 == 0

        if self.memoization:
            if (i,f) in self.dict_fxn_t_bar_ma:
                return self.dict_fxn_t_bar_ma[(i,f)]

        if f > 0:
            omega_i = self.omega[i]
            alpha = self.alpha
            releases_to_s_n = f-1

            omega_final = math.sqrt(omega_i**2 + 2*alpha*releases_to_s_n)

            miat_minutes = (omega_final - omega_i) / alpha
        else:
            miat_minutes = 0

        if self.memoization:
            self.dict_fxn_t_bar_ma[(i,f)] = miat_minutes

        assert miat_minutes >= 0

        return miat_minutes

    def fxn_t_bar_min_index_link(self,i,j):

        """MIAT (in minutes) to travel from s_n in \\Omega_{i}^rR(i,j) to s_1 in \\Omega_{j}^rf"""

        if USE_OMEGA_ASSERTS:
            assert not self.fxn_assert_omega_indices(i,j)

        if self.memoization:
            if (i,j) in self.dict_fxn_t_bar_min_index_link:
                return self.dict_fxn_t_bar_min_index_link[(i,j)]

        omega_i = self.omega[i]

        r_ij = self.fxn_r(i,j)
        f = r_ij

        reps = f-1

        alpha = self.alpha

        s_n = math.sqrt(omega_i**2+2*alpha*reps)

        s_1 = self.omega[j]

        miat_minutes = self.fxn_t_bar_min_rpm(s_n,s_1)

        if self.memoization:
            self.dict_fxn_t_bar_min_index_link[(i,j)] = miat_minutes

        return miat_minutes

    def fxn_is_reachable(self,s_b,s_a):

        """Get whether s_b is reachable from s_a"""

        if USE_OMEGA_ASSERTS:
            assert not self.fxn_assert_omega_rpms(s_b,s_a)

        if math.sqrt(s_a**2 + 2*(-self.alpha)) <= s_b and s_b <= math.sqrt(s_a**2 + 2*(self.alpha)):

            return 1

        return 0

    def fxn_miat_min(self,seq):

        """Get MIAT of sequence seq in min"""

        alpha = self.alpha

        l = len(seq)

        if l == 0:
            return 0

        miat_sum_minutes = 0

        for i in range(l-1):

            s_1 = seq[i]
            s_2 = seq[i+1]
            t_bar_min_rpm_val = self.fxn_t_bar_min_rpm(s_1,s_2)
            miat_sum_minutes += t_bar_min_rpm_val

        s_n = seq[l-1]
        t_bar_min_rpm_final_val = self.fxn_t_bar_min_rpm(s_n,math.sqrt(s_n**2+2*alpha))
        miat_sum_minutes += t_bar_min_rpm_final_val

        return miat_sum_minutes

    def fxn_demand(self,seq,use_irf):

        """Get sequence demand"""

        if use_irf:

            return self.fxn_demand_irf(seq)

        else:

            return self.fxn_demand_rpm_seq(seq)

    def fxn_demand_irf(self,sub_seq_irf):

        """Get demand of dominant sequence"""

        # assert len(sub_seq_irf) == 3

        if self.memoization:

            i = sub_seq_irf[0]
            r = sub_seq_irf[1]
            f = sub_seq_irf[2]

            if (i,r,f) in self.dict_fxn_demand_irf:
                return self.dict_fxn_demand_irf[(i,r,f)]

        demand_sum_us = 0

        demand_sum_us = self.fxn_d_irf(sub_seq_irf)

        if self.memoization:
            self.dict_fxn_demand_irf[(i,r,f)] = demand_sum_us

        return demand_sum_us

    def fxn_demand_rpm_seq(self,seq):

        """Get demand of speed sequence"""

        if len(seq) == 0:
            return 0

        demand_sum_us = 0

        for s in seq:

            demand_sum_us += self.fxn_c(s)

        return demand_sum_us

    def fxn_omega_rb(self,i,r):

        """Create RB sequence"""

        assert i >= 1
        assert i <= self.m
        assert r >= 0

        assert i % 1 == 0
        assert r % 1 == 0

        rb_seq = [self.omega[i]]*r

        return rb_seq

    def fxn_omega_ma(self,i,f):

        """Create MA sequence"""

        assert i >= 1
        assert i <= self.m
        assert f >= 0

        assert i % 1 == 0
        assert f % 1 == 0

        ma_seq = []

        if f == 0:

            pass

        elif f > 0 and 1 <= i <= self.m:

            omega_i = self.omega[i]
            alpha = self.alpha

            r_im = self.fxn_r(i,self.m)
            f_im_max = r_im

            #Subtract 1 from reps to account for k=0 counting towards the # reps
            reps = min(f,f_im_max)

            for k in range(1,reps+1):

                ma_seq+=[math.sqrt(omega_i**2+2*alpha*(k-1))]

        return ma_seq

    def fxn_r(self,i,j):

        """Get # releases between \\omega_i and \\omega_j"""

        if USE_OMEGA_ASSERTS:
            assert not self.fxn_assert_omega_indices(i,j)

        if self.memoization:
            if (i,j) in self.dict_fxn_r_ij:
                return self.dict_fxn_r_ij[(i,j)]

        if 0 < i < j:

            theta = self.fxn_theta(i,j)

            output = math.ceil(theta)

        else:

            output = 0

        if self.memoization:
            self.dict_fxn_r_ij[(i,j)] = output

        return output

    def fxn_omega_irf(self,i,r,f):

        """Create RB-MA sequence"""

        assert i >= 1
        assert i <= self.m
        assert r >= 0
        assert f >= 0

        assert i % 1 == 0
        assert r % 1 == 0
        assert f % 1 == 0

        rb_seq = self.fxn_omega_rb(i,r)

        ma_seq = self.fxn_omega_ma(i,f)

        rbma_seq = rb_seq + ma_seq

        return rbma_seq

    def fxn_create_speed_seq(self,i,r,f,use_irf):

        """Create speed sequence in truncated or expanded form"""

        if use_irf: #Truncated
            seq = [i,r,f]
        else: #Expanded
            seq = self.fxn_omega_irf(i,r,f)

        return seq

    def fxn_s_irf(self,i_arr,r_arr,f_arr):

        """Create chained RB-MA sequences"""

        i_length = len(i_arr)
        q = i_length
        r_length = len(r_arr)
        f_length = len(f_arr)

        assert r_length == q
        assert f_length == q

        for x in range(q-1):
            assert i_arr[x]<=i_arr[x+1]
            r_arr_x_x_to_xp1 = self.fxn_r(i_arr[x],i_arr[x+1])
            assert f_arr[x]==r_arr_x_x_to_xp1

        for x in range(q):
            assert r_arr[x] >= 0

        assert f_arr[q] >= 0

        s_omega_seq = []

        for x in range(q):

            i=i_arr[x]
            r=r_arr[x]
            f=f_arr[x]

            rbma_seq = self.fxn_omega_irf(i,r,f)
            s_omega_seq += rbma_seq

    def fxn_t_ib(self,i,b,use_irf,eliminate_bad_solutions=True):

        """Get MIAT of all sequences beginning with \\omega_1 thru \\omega_m and D(S)>=b"""

        if USE_ASSERTS:
            assert i >= 1
            assert i <= self.m
            assert b >= 0

            assert i % 1 == 0
            assert b % 1 == 0

        if b == 0:
            return (0,0)

        seq_set = self.fxn_s_ib(i,b,use_irf,eliminate_bad_solutions)

        seq_set_length = len(seq_set)

        if USE_ASSERTS:
            assert seq_set_length
            assert len(seq_set[0])
            if use_irf:
                assert len(seq_set[0][0]) == 3


        miat_min_array = [0]*seq_set_length

        for x in range(seq_set_length):

            if use_irf:
                seq_miat = self.fxn_t_bar_min_irf_arr(seq_set[x])
            else:
                seq_miat = self.fxn_miat_min(seq_set[x])
            miat_min_array[x] = seq_miat

        if not miat_min_array:

            miat_min = math.inf

        else:

            miat_min = min(miat_min_array)

        sln_index = miat_min_array.index(miat_min)
        sln_seq = seq_set[sln_index]

        miat_us = self.fxn_min_to_us(miat_min)

        return (miat_us,sln_seq)

    def fxn_s_ib(self,i,b,use_irf,eliminate_bad_solutions=True):

        """Get all sequences beginning with \\omega_1 thru \\omega_m and D(S)>=b"""

        if USE_ASSERTS:

            assert i >= 1
            assert i <= self.m
            assert b >= 0

            assert i % 1 == 0
            assert b % 1 == 0

        seq_set_i_b = []

        if b > 0:

            for x in range(1,i+1):
                seq_set_i_b_single = self.fxn_s_ib_single_i(x,b,use_irf,eliminate_bad_solutions)
                seq_set_i_b += seq_set_i_b_single

        return seq_set_i_b

    def fxn_s_ib_single_i(self,i,b,use_irf,eliminate_bad_solutions=True):

        """Get the set of seq with s_1 = \\omega_i, D(S) >= b"""

        if USE_ASSERTS:

            assert i >= 1
            assert i <= self.m

            assert i % 1 == 0
            assert b % 1 == 0

        if b <= 0:

            return []

        if self.memoization and b > 0:
            if (i,b) in self.dict_fxn_s_ib_single:
                return self.dict_fxn_s_ib_single[(i,b)]

        seq_set_i_b_single_f_iterating = self.fxn_s_ib_single_f_iterating(i,b,use_irf,eliminate_bad_solutions)
        seq_set_i_b_single_j_iterating = self.fxn_s_ib_single_j_iterating(i,b,use_irf,eliminate_bad_solutions)

        output = seq_set_i_b_single_f_iterating + seq_set_i_b_single_j_iterating

        if eliminate_bad_solutions:
            output_actual = self.fxn_eliminate_bad_solutions(output,use_irf)
        else:
            output_actual = output

        if self.memoization and b > 0:
            self.dict_fxn_s_ib_single[(i,b)] = output_actual

        return output_actual

    def fxn_s_ib_single_f_iterating(self,i,b,use_irf,eliminate_bad_solutions):

        """Find a sequence with minimum interarrival time which begins with speed \\omega_i,
        is NOT composed of a subsequence starting at another boundary speed, and generates demand b"""

        output = []

        c_m = self.wcet[-1]

        f_max_by_r_im = self.fxn_r(i,self.m)
        f_max_by_wcet = math.ceil(b/c_m)
        max_f = min(f_max_by_wcet, f_max_by_r_im)

        for f in range(0,max_f+1):

            seq_irf_f_only = self.fxn_create_speed_seq(i,0,f,use_irf)

            d_f = self.fxn_demand(seq_irf_f_only,use_irf)

            d_remaining = b - d_f

            if d_remaining > 0:

                c_i = self.wcet[i]

                r_min = math.ceil(d_remaining/c_i)

                seq_proposed = self.fxn_create_speed_seq(i,r_min,f,use_irf)

                d_seq_proposed = self.fxn_demand(seq_proposed,use_irf)

                if USE_ASSERTS:
                    assert d_seq_proposed >= b
                    assert d_seq_proposed - c_i < b

                seq_irf = seq_proposed

            else:

                seq_irf = seq_irf_f_only

            if use_irf:
                output += [[seq_irf]]
            else:
                output += [seq_irf]

        if eliminate_bad_solutions:
            output_actual = self.fxn_eliminate_bad_solutions(output,use_irf)
        else:
            output_actual = output

        return output_actual

    def fxn_s_ib_single_j_iterating(self,i,b,use_irf,eliminate_bad_solutions):

        """Find a sequence with minimum interarrival time which begins with speed \\omega_i,
        IS composed of a subsequence starting at another boundary speed, and generates demand b"""

        output = []

        c_i = self.wcet[i]

        for j in range(i+1,self.m+1):

            f_i_to_j = self.fxn_r(i,j)

            seq_f_i_to_j_only = self.fxn_create_speed_seq(i,0,f_i_to_j,use_irf)

            d_f_i_to_j_only = self.fxn_demand(seq_f_i_to_j_only,use_irf)

            d_remaining_for_r = b - d_f_i_to_j_only

            r_max = math.ceil(d_remaining_for_r/c_i)

            for r in range(0,r_max+1):

                omega_r_rij = self.fxn_create_speed_seq(i,r,f_i_to_j,use_irf)

                d_omega_r_rij = self.fxn_demand(omega_r_rij,use_irf)

                d_remaining_for_s_ib = b - d_omega_r_rij

                seq_set_i_single_remaining = self.fxn_s_ib_single_i(j,d_remaining_for_s_ib,use_irf)

                for seq_remain in seq_set_i_single_remaining:

                    if use_irf:
                        assert omega_r_rij[0] != seq_remain[0][0]
                        output += [[omega_r_rij] + seq_remain]
                    else:
                        output += [omega_r_rij + seq_remain]

        if eliminate_bad_solutions:
            output_actual = self.fxn_eliminate_bad_solutions(output,use_irf)
        else:
            output_actual = output

        return output_actual

    def fxn_eliminate_bad_solutions(self,input_seqs,use_irf):

        """Given a list of candidate speed sequences, return only the seq with min interarrival time"""

        if input_seqs == []:
            return []

        #Output Processing
        output_miat_only = []

        if use_irf:
            miat_array = list(map(self.fxn_t_bar_min_irf_arr,input_seqs))
        else:
            miat_array = list(map(self.fxn_miat_min,input_seqs))

        miat = min(miat_array)
        output_index_with_miat = miat_array.index(miat)

        output_miat_only = [input_seqs[output_index_with_miat]]

        output_actual = output_miat_only

        return output_actual

## Approximation Functions

    def fxn_set_r_prime(self,b,i,e_r):

        """Get approximated set of values for r"""

        assert i >= 1
        assert i <= self.m
        assert b >= 0
        assert e_r > 0
        assert e_r < 1

        assert i % 1 == 0
        assert b % 1 == 0

        r_p = []

        c_i = self.wcet[i]

        ell_r = -math.log(math.ceil(b/c_i)) / math.log(1-e_r)

        for k in range(0,math.floor(ell_r)+1+1):

            apx_value = self.fxn_log_apx(b,c_i,e_r,k)

            r_p += [apx_value]

        return r_p

    def fxn_set_f_prime(self,b,e_f):

        """Get approximated set of values for f"""

        assert b >= 0
        assert e_f > 0
        assert e_f < 1

        assert b % 1 == 0

        f_p = []

        c_m = self.wcet[-1]

        ell_f = -math.log(math.ceil(b/c_m)) / math.log(1-e_f)

        for k in range(0,math.floor(ell_f)+1+1):

            apx_value = self.fxn_log_apx(b,c_m,e_f,k)

            f_p += [apx_value]

        return f_p

    def fxn_log_apx(self,b,c,e_x,k):

        """Get log approximation # of reps given values b, c, \\epsilon_x, and k"""

        assert c >= 1
        assert c <= self.wcet[1]
        assert c >= self.wcet[-1]
        assert b >= 0
        assert k >= 0
        assert e_x > 0
        assert e_x < 1

        assert b % 1 == 0
        assert c % 1 == 0
        assert k % 1 == 0

        ceil_part = math.ceil(b/c)
        epsilon_part = (1-e_x)**k

        output = math.floor(ceil_part * epsilon_part)

        return output

    def fxn_create_k_apx(self,e_b,b):

        """Get K scalar for approximation of b"""

        assert b >= 0
        assert e_b > 0
        assert e_b < 1

        assert b % 1 == 0

        self.k =  e_b * b / self.m

    def fxn_demand_apx(self,seq,use_irf):

        """Get approximate demand after scalar K division"""

        assert self.k != -1

        d = self.fxn_demand(seq,use_irf)

        d_apx = math.floor(d/self.k)

        return d_apx

    def fxn_t_ib_apx(self,i,b,apx_instance,use_irf,eliminate_bad_solutions=True):

        """Get MIAT of all sequences beginning with \\omega_1 thru \\omega_m and D(S)>=b"""

        assert i >= 1
        assert i <= self.m
        assert b >= 0

        assert i % 1 == 0
        assert b % 1 == 0

        if b == 0:
            return (0,0,0)

        #Extract e_b, approximate b
        e_b = apx_instance.epsilon_b
        self.fxn_create_k_apx(e_b,b)
        b_prime = math.floor(b/self.k)

        seq_set = self.fxn_s_ib_apx(i,b_prime,apx_instance,use_irf,eliminate_bad_solutions)

        seq_set_length = len(seq_set)
        assert seq_set_length
        assert len(seq_set[0])
        if use_irf:
            assert len(seq_set[0][0]) == 3


        miat_min_array = [0]*seq_set_length

        for x in range(seq_set_length):

            if use_irf:
                seq_miat = self.fxn_t_bar_min_irf_arr(seq_set[x])
            else:
                seq_miat = self.fxn_miat_min(seq_set[x])
            miat_min_array[x] = seq_miat

        if not miat_min_array:

            miat_min = math.inf

        else:

            miat_min = min(miat_min_array)

        sln_index = miat_min_array.index(miat_min)
        sln_seq = seq_set[sln_index]

        miat_us = self.fxn_min_to_us(miat_min)

        b_safe = self.k*b_prime /(apx_instance.one_minus_epsilon)

        self.fxn_reset_k_and_k_based_tables()

        return (miat_us,sln_seq,b_safe)

    def fxn_s_ib_apx(self,i,b,apx_instance,use_irf,eliminate_bad_solutions=True):

        """Get all sequences beginning with \\omega_1 thru \\omega_m and D(S)>=b"""

        assert i >= 1
        assert i <= self.m
        assert b >= 0

        assert i % 1 == 0
        assert b % 1 == 0

        seq_set_i_b = []

        if b > 0:

            for x in range(1,i+1):

                seq_set_i_b_single = self.fxn_s_ib_single_i_apx(x,b,apx_instance,use_irf,eliminate_bad_solutions)
                seq_set_i_b += seq_set_i_b_single

        return seq_set_i_b

    def fxn_s_ib_single_i_apx(self,i,b,apx_instance,use_irf,eliminate_bad_solutions=True):

        """Get the set of seq with s_1 = \\omega_i, D(S) >= b"""

        assert i >= 1
        assert i <= self.m

        assert i % 1 == 0
        assert b % 1 == 0

        if b <= 0:

            return []

        if self.memoization and b > 0:
            if (i,b) in self.dict_fxn_s_ib_single_i_apx:
                return self.dict_fxn_s_ib_single_i_apx[(i,b)]

        #Deconstruct APX
        e_r = apx_instance.epsilon_r
        e_f = apx_instance.epsilon_f

        seq_set_i_b_single = []
        seq_set_i_single_remaining = []

        if b > 0 and i == self.m:

            c_i = self.wcet[i]

            b_inflated = b + 1

            b_adjusted = math.ceil(b_inflated * self.k)

            r_min = math.ceil(b_adjusted/c_i)

            seq_proposed = self.fxn_create_speed_seq(i,r_min,0,use_irf)

            d_seq_proposed = self.fxn_demand_apx(seq_proposed,use_irf)

            assert d_seq_proposed >= b
            assert d_seq_proposed - c_i < b

            if use_irf:
                output = [[seq_proposed]]
            else:
                output = [seq_proposed]

        if b > 0 and i < self.m:

            #Single boundary speed solutions

            f_p = self.fxn_set_f_prime(b,e_f)

            for f in f_p:

                seq_irf_f_only = self.fxn_create_speed_seq(i,0,f,use_irf)

                d_f = self.fxn_demand_apx(seq_irf_f_only,use_irf)

                b_inflated = b + 1
                b_adjusted = math.ceil(b_inflated * self.k)
                d_r_min = b_adjusted - d_f

                if d_r_min > 0:

                    c_i = self.wcet[i]

                    r_min = math.ceil(d_r_min/c_i)

                    seq_proposed = self.fxn_create_speed_seq(i,r_min,f,use_irf)

                    d_seq_proposed = self.fxn_demand_apx(seq_proposed,use_irf)

                    assert d_seq_proposed >= b

                    seq_irf = seq_proposed

                else:

                    seq_irf = seq_irf_f_only

                if use_irf:
                    seq_set_i_b_single += [[seq_irf]]
                else:
                    seq_set_i_b_single += [seq_irf]

            #Multiple boundary speed solutions
            r_p = self.fxn_set_r_prime(b,i,e_r)

            for r in r_p:

                for j in range(i+1,self.m+1):

                    r_ij = self.fxn_r(i,j)
                    f_i_to_j = r_ij

                    omega_r_rij = self.fxn_create_speed_seq(i,r,f_i_to_j,use_irf)

                    d_omega_r_rij = self.fxn_demand_apx(omega_r_rij,use_irf)

                    b_r = b - d_omega_r_rij

                    seq_set_i_single_remaining = self.fxn_s_ib_single_i_apx(j,b_r,apx_instance,use_irf,eliminate_bad_solutions)

                    for seq_remain in seq_set_i_single_remaining:

                        if use_irf:
                            assert omega_r_rij[0] != seq_remain[0][0]
                            seq_set_i_b_single += [[omega_r_rij] + seq_remain]
                        else:
                            seq_set_i_b_single += [omega_r_rij + seq_remain]

            output = seq_set_i_b_single

        if eliminate_bad_solutions:
            #Output Processing
            output_miat_only = []

            n_sequences = len(output)

            if n_sequences > 0:

                miat_array = [math.inf]*n_sequences

                for x in range(n_sequences):

                    if use_irf:
                        miat_array[x] = self.fxn_t_bar_min_irf_arr(output[x])
                    else:
                        miat_array[x] = self.fxn_miat_min(output[x])

                miat = min(miat_array)
                output_index_with_miat = miat_array.index(miat)

                output_miat_only = [output[output_index_with_miat]]

            output_actual = output_miat_only

        else:

            output_actual = output

        if self.memoization and b > 0:
            self.dict_fxn_s_ib_single_i_apx[(i,b)] = output_actual

        return output_actual

## Helper Functions not found in paper

    def t_bar_final_us(self,i):

        """Get miat when accelerating maximally from \\omega_i for one rev"""

        assert i >= 1
        assert i <= self.m

        assert i % 1 == 0

        next_speed_max_accel = math.sqrt(self.omega[i]**2 + 2*self.alpha)

        next_speed_max_accel = min(self.omega[-1],next_speed_max_accel)

        miat_minutes = self.fxn_t_bar_min_rpm(self.omega[i],next_speed_max_accel)

        miat_us = self.fxn_min_to_us(miat_minutes)

        return miat_us

    def fxn_min_to_us(self,minutes):

        """Get equivalent microseconds given minutes"""

        assert minutes >= 0

        #us = min * 60s/min * 1000 ms / s * 1000us/ms = 60*1000*1000 us
        us = minutes * 60 * 1000 * 1000

        return us

    def is_feasible(self):

        """Get whether accel values or util makes model infeasible on uniprocessor"""

        if self.alpha <= 0:

            return False

        highest_util = self.get_max_mode_utilization()

        if highest_util <= 1:

            return True

        return False

    def print_parameters(self):

        """Print Model Parameters"""

        print("AVR Task Params")

        print("M:",self.m)

        print("W:",self.omega)

        print("C:",self.wcet)

        print("A:",self.alpha)

    def calc_mode_utilizations(self):

        """Get max utilizations for all modes"""

        m = self.m

        assert m > 1

        self.mode_utils = [0]*(m+1)

        for i in range(1,m+1):

            self.mode_utils[i] = self.wcet[i]/self.t_bar_final_us(i)

    def get_max_mode_utilization(self):

        """Get max utilization of any mode"""

        self.calc_mode_utilizations()

        return max(self.mode_utils)

    def print_mode_utilizations(self):

        """Print all mode utilizations calculations"""

        if self.mode_utils[0] == -1:

            self.calc_mode_utilizations()

        for i in range(1,self.m+1):

            print(self.wcet[i],"us /",self.t_bar_final_us(i)," us = ",self.mode_utils[i],"%")

    ## Memoization functions
    def disable_memoization(self):

        """Disable Memoization"""

        self.memoization = False

## Analytic MIAT Functions

    def fxn_t_rb_ir(self,i,r):

        """Get MIAT for \\omega_{RB}(i,r) sequence"""

        if r > 0:

            t_bar_i_to_i = self.fxn_t_bar_min_index(i,i)

            miat_minutes = (r-1) * t_bar_i_to_i

        else:

            miat_minutes = 0

        return miat_minutes

    def fxn_t_ma_if(self,i,f):

        """Get MIAT of \\omega_ma_if"""

        if f > 0:

            omega_i = self.omega[i]
            alpha = self.alpha

            miat_minutes = (math.sqrt(omega_i**2 + 2*alpha*(f-1)) - omega_i)/alpha

        else:

            miat_minutes = 0

        return miat_minutes

    def fxn_t_rm_irf(self,i,r,f):

        """Get MIAT for s_n \\in \\omega_{RB}(i,r) to s_1 \\in \\omega_{MA}(i,f)"""

        if r > 0 and f > 0:

            miat_minutes = self.fxn_t_bar_min_index(i,i)

        else:

            miat_minutes = 0

        return miat_minutes

    def fxn_t_irf(self,i,r,f):

        """Get MIAT of \\Omega_{i}^{r,f}"""

        t_rb = self.fxn_t_rb_ir(i,r)
        t_l_rm = self.fxn_t_rm_irf(i,r,f)
        t_ma = self.fxn_t_ma_if(i,f)

        miat_minutes = t_rb + t_l_rm + t_ma

        return miat_minutes

    def fxn_t_l_irfj(self,i,r_i,f_i,j):

        """Get MIAT between s_n of \\Omega_{i}^{r_i,f_i} and \\Omega_{j}^{r_j,f_j}"""

        omega_j = self.omega[j]

        s_1 = self.fxn_s_n_in_omega_irf(i,r_i,f_i)
        s_2 = omega_j

        miat_minutes = self.fxn_t_bar_min_rpm(s_1,s_2)

        return miat_minutes

    def fxn_t_f_irf(self,i,r,f):

        """Get MIAT for last job release at speed s_n \\in \\Omega_i^{r,f}"""

        s_1 = self.fxn_s_n_in_omega_irf(i,r,f)
        alpha = self.alpha
        s_2 = math.sqrt(s_1**2+2*alpha)

        t_bar_s1_s2 = self.fxn_t_bar_min_rpm(s_1,s_2)

        miat_minutes = t_bar_s1_s2

        return miat_minutes

    def fxn_s_n_in_omega_irf(self,i,r,f):

        """Get s_n \\in \\omega_i^{rf}"""

        if r == 0 and f == 0:

            output = None

        elif r > 0 and f == 0:

            output = self.omega[i]

        elif f > 0:

            output = math.sqrt(self.omega[i]**2+2*self.alpha*(f-1))

        else:

            assert 0

        return output

    def fxn_t_irf_arr(self,irf_arr):

        """Get MIAT for S_{i}^{r,f} array"""

        q = len(irf_arr)

        assert q > 0

        if q == 1:

            i = irf_arr[0][0]
            r = irf_arr[0][1]
            f = irf_arr[0][2]

            t_irf = self.fxn_t_irf(i,r,f)
            t_f_irf = self.fxn_t_f_irf(i,r,f)

            miat_minutes = t_irf + t_f_irf

        if q > 1:

            miat_minutes = 0

            for x in range(q-1):

                i = irf_arr[x][0]
                r = irf_arr[x][1]
                f = irf_arr[x][2]
                j = irf_arr[x+1][0]

                t_irf = self.fxn_t_irf(i,r,f)
                t_l_irfj = self.fxn_t_l_irfj(i,r,f,j)

                miat_local_minutes = t_irf + t_l_irfj

                miat_minutes += miat_local_minutes

            i_q = irf_arr[q-1][0]
            r_q = irf_arr[q-1][1]
            f_q = irf_arr[q-1][2]

            t_irf = self.fxn_t_irf(i_q,r_q,f_q)
            t_f_irf = self.fxn_t_f_irf(i_q,r_q,f_q)

            miat_minutes += t_irf + t_f_irf

        return miat_minutes

## Analytic MIAT Helper Functions

    def fxn_miat_t_i_b_single(self,i,b):

        """Get MIAT for all dominant sequences with s_1 = \\omega_i and D(S) >= b """

        miat_minutes = math.inf
        miat_seq = [[-1]]

        assert i >= 1
        assert i <= self.m

        assert b % 1 == 0

        if self.memoization and b > 0:
            if (i,b) in self.dict_fxn_miat_t_i_b_single:
                return self.dict_fxn_miat_t_i_b_single[(i,b)]

        if b <= 0 :

            miat_minutes = 0
            miat_seq = [[]]
            output = (miat_minutes,miat_seq)

        if b > 0 and i == self.m:

            c_i = self.wcet[i]
            r_min = math.ceil(b/c_i)

            seq_proposed = [i,r_min,0]

            miat_minutes_proposed = self.fxn_t_bar_min_irf(seq_proposed)

            d_proposed_seq = self.fxn_demand(seq_proposed,True)

            assert d_proposed_seq >= b
            assert d_proposed_seq - c_i < b

            miat_minutes = miat_minutes_proposed
            miat_seq = [seq_proposed]

        if b > 0 and i < self.m:

            #Single boundary speed solutions

            f_max_by_r_im = self.fxn_r(i,self.m)
            f_max_by_wcet = math.ceil(b/self.wcet[-1])
            max_f = min(f_max_by_wcet, f_max_by_r_im)

            for f in range(0,max_f+1):

                seq_irf_f_only = [i,0,f]
                d_f = self.fxn_demand(seq_irf_f_only,True)

                d_r_min = b-d_f

                if d_r_min > 0:

                    c_i = self.wcet[i]

                    r_min = math.ceil(d_r_min/c_i)

                    proposed_seq = [i,r_min,f]

                    d_proposed_seq = self.fxn_demand(proposed_seq,True)

                    assert d_proposed_seq >= b
                    assert d_proposed_seq - c_i < b

                    seq_irf = proposed_seq

                else:

                    seq_irf = seq_irf_f_only

                miat_local = self.fxn_t_bar_min_irf(seq_irf)

                if miat_local < miat_minutes:

                    miat_minutes = miat_local
                    miat_seq = [seq_irf]

            #Multiple boundary speed solutions
            r_max = math.ceil(b/c_i)

            for r in range(r_max+1):

                for j in range(i+1,self.m+1):

                    #Get # reps for valid seq from \\Omega_{i}^{rf} to \\Omega_{j}^{??}
                    r_ij = self.fxn_r(i,j)
                    f_i_to_j = r_ij

                    omega_r_rij_irf = [i,r,f_i_to_j]

                    #Get MIAT for \\Omega_{i}^{r,R(i,j)-1}
                    miat_seq_omega_r_rij_irf = self.fxn_t_bar_min_irf(omega_r_rij_irf)

                    #Get MIAT from s_n of \\Omega_{i}^{r,R(i,j)-1} to s_1 of \\Omega_{j}^{??}
                    miat_seq_omega_rij_irf_link = self.fxn_t_bar_min_index_link(i,j)

                    #Calculate demand of \\Omega_{i}^{rf}
                    d_omega_r_rij = self.fxn_demand(omega_r_rij_irf,True)

                    #Calculate the remaining demand required, b_r
                    b_r = b - d_omega_r_rij

                    #Calculate MIAT and corresponding sequence starting at j with D(S) >= b_r
                    (miat_tjb_r,seq_tjb_r) = self.fxn_miat_t_i_b_single(j,b_r)

                    #Get current MIAT by summing all pieces
                    miat_local = miat_seq_omega_r_rij_irf + miat_seq_omega_rij_irf_link + miat_tjb_r

                    #If MIAT is lower than current lowest...
                    if miat_local < miat_minutes:

                        #Log the local MIAT and solution
                        miat_minutes = miat_local
                        miat_seq = [seq_irf + seq_tjb_r]

        output = (miat_minutes,miat_seq)

        if self.memoization and b > 0:
            self.dict_fxn_miat_t_i_b_single[(i,b)] = output

        return (miat_minutes,miat_seq)

    def fxn_miat_t_i_b(self,i,b):

        """Get MIATs for all sequences with s_1 = \\omega_1 through \\omega_i and D(S) >= b"""

        assert i >= 1
        assert i <= self.m
        assert b >= 0

        assert i % 1 == 0
        assert b % 1 == 0

        miat_seq_dict = { math.inf : [[0,0,0]]}

        if b > 0:

            for x in range(1,i+1):

                (miat_t_i_b,seq_t_i_b) = self.fxn_miat_t_i_b_single(x,b)
                miat_seq_dict[miat_t_i_b] = seq_t_i_b

        miat_actual = min(miat_seq_dict)
        miat_actual_us = self.fxn_min_to_us(miat_actual)
        seq_miat_actual = miat_seq_dict[miat_actual]

        return (miat_actual_us,seq_miat_actual)

    def fxn_reset_k_and_k_based_tables(self):

        """Clear k-dependent hash tables"""

        self.k = -1

        self.dict_fxn_s_ib_single_i_apx.clear()

    def fxn_reset_all_tables(self):

        """Clear all hash tables"""

        self.dict_fxn_c.clear()
        self.dict_fxn_s_ib_single.clear()
        self.dict_fxn_demand_irf.clear()
        self.dict_fxn_t_bar_min_irf.clear()
        self.dict_fxn_demand_if.clear()
        self.dict_fxn_t_bar_ma.clear()
        self.dict_fxn_r_ij.clear()
        self.dict_fxn_t_bar_min_index_link.clear()
        self.dict_fxn_t_bar_min_index.clear()
        self.dict_fxn_miat_t_i_b_single.clear()
        self.dict_fxn_s_ib_single_i_apx.clear()

if __name__ == '__main__':

    #Unit Tests
    UT_OMEGA = [0,1,2,3,4,5]
    UT_WCET = [0,50,40,30,20,10]
    UT_ALPHA = 10
    UT_M = len(UT_OMEGA)-1
    UT_AVR_TSK = AvrTask(UT_M,UT_OMEGA,UT_WCET,UT_ALPHA,"unit_test")

    # def fxn_assert_omega_indices(self,i,j):
    UT_AVR_TSK.fxn_assert_omega_indices(1,2)

    # def fxn_assert_omega_rpms(self,omega_i,omega_j):
    UT_AVR_TSK.fxn_assert_omega_indices(4,5)

    # def fxn_c(self,s):
    retval = UT_AVR_TSK.fxn_c(2.5)
    assert retval == 30

    # def fxn_c_binary(self,s):
    retval = UT_AVR_TSK.fxn_c_binary(2.5)
    assert retval == 30

    # def fxn_c_linear(self,s):
    retval = UT_AVR_TSK.fxn_c_binary(2.5)
    assert retval == 30

    # def fxn_theta(self,i,j):
    retval = UT_AVR_TSK.fxn_theta(1,2)
    assert retval == (UT_OMEGA[2]**2 - UT_OMEGA[1]**2)/(2*UT_ALPHA)

    # def fxn_t_min_idx(self,i,j):
    retval = UT_AVR_TSK.fxn_t_min_idx(1,2)
    assert retval == UT_AVR_TSK.fxn_t_min_rpm(UT_OMEGA[1],UT_OMEGA[2])

    # def fxn_t_min_rpm(self,omega_i,omega_j):
    retval = UT_AVR_TSK.fxn_t_min_rpm(1,2)
    assert retval == (math.sqrt(2*2**2 + 4*UT_ALPHA + 2*1**2) - 2 - 1)/UT_ALPHA

    # def fxn_omega_rb(self,i,r):
    retval = UT_AVR_TSK.fxn_omega_rb(2,12)
    assert retval == [UT_OMEGA[2]]*12

    # def fxn_omega_ma(self,i,f):
    retval = UT_AVR_TSK.fxn_omega_ma(2,2)
    assert retval == [UT_OMEGA[2],
                        math.sqrt(UT_OMEGA[2]**2+2*UT_ALPHA*1)]

    # def fxn_r(self,i,j):
    retval = UT_AVR_TSK.fxn_r(2,UT_AVR_TSK.m)
    assert retval == math.ceil(UT_AVR_TSK.fxn_theta(2,UT_AVR_TSK.m))

    # def fxn_omega_irf(self,i,r,f):
    retval = UT_AVR_TSK.fxn_omega_irf(2,12,2)
    rb = [UT_OMEGA[2]]*12
    ma = [UT_OMEGA[2],
            math.sqrt(UT_OMEGA[2]**2+2*UT_ALPHA*1)]
    assert retval == (rb + ma)

    #MIAT methods comparison
    miat_seq_irf_elim = UT_AVR_TSK.fxn_t_ib(UT_AVR_TSK.m,200,True,True)
    UT_AVR_TSK.fxn_reset_all_tables()
    miat_seq_elim = UT_AVR_TSK.fxn_t_ib(UT_AVR_TSK.m,200,False,True)
    UT_AVR_TSK.fxn_reset_all_tables()
    miat_seq_none = UT_AVR_TSK.fxn_t_ib(UT_AVR_TSK.m,200,False,False)
    UT_AVR_TSK.fxn_reset_all_tables()
    assert miat_seq_irf_elim[0] == miat_seq_elim[0]
    assert miat_seq_elim[0] == miat_seq_none[0]

    # def fxn_reset_k_and_k_based_tables(self):
    UT_AVR_TSK.k = 500
    UT_AVR_TSK.fxn_reset_k_and_k_based_tables()
    assert UT_AVR_TSK.k == -1
